from dataclasses import dataclass
import struct
from PIL import Image
from enum import IntEnum


def rgb565_to_rgb888(rgb565: int) -> tuple[int, int, int]:
    red = ((rgb565 >> 11) * 255 + 15) // 31
    green = (((rgb565 >> 5) & 0x3F) * 255 + 31) // 63
    blue = ((rgb565 & 0x1F) * 255 + 15) // 31
    return (red, green, blue)


def rgb888_to_rgb565(r: int, g: int, b: int) -> int:
    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return rgb565


class BlockType(IntEnum):
    Preview = 1
    Background = 2
    HoursArm = 3
    MinutesArm = 4
    SecondsArm = 5
    Year = 6
    Month = 7
    Day = 8
    Hours = 9
    Minutes = 10
    Seconds = 11
    AmPm = 12
    WeekDay = 13
    Steps = 14
    HeartRate = 15
    Calories = 16
    Distance = 17
    Unknown1 = 22
    Animation = 23
    Battery = 24
    StepsStrip = 30
    HeartRateStrip = 33
    DistanceLabel = 37
    HoursDigitTens = 39
    HoursDigitOnes = 40
    MinutesDigitTens = 41
    MinutesDigitOnes = 42

    def __str__(self):
        return self.name


class BlockHorizontalAlignment(IntEnum):
    NotSpecified = 0
    Left = 9
    Center = 10
    Right = 12


@dataclass
class Header:
    num_img_info_size: int
    num_blocks: int
    dnk: int
    _struct = struct.Struct("<HBB")
    size = _struct.size

    def __post_init__(self):
        object.__setattr__(
            self,
            "_bytes",
            self._struct.pack(self.num_img_info_size, self.num_blocks, self.dnk),
        )

    def __bytes__(self):
        return self._bytes

    @staticmethod
    def loads(data: bytes):
        assert len(data) == Header.size
        num_img_size_info, num_blocks, dnk = Header._struct.unpack(data)
        return Header(num_img_size_info, num_blocks, dnk)


@dataclass
class BlockInfo:
    img_offset: int
    img_id: int
    width: int
    height: int
    pos_x: int
    pos_y: int
    num_imgs: int
    is_rgba: bool
    blocktype: BlockType
    align: BlockHorizontalAlignment
    compr: int
    cent_x: int
    cent_y: int
    _struct = struct.Struct("<IHHHHHBBBBBB")
    size = _struct.size

    def __post_init__(self):
        object.__setattr__(
            self,
            "_bytes",
            self._struct.pack(
                self.img_offset,
                self.img_id,
                self.width,
                self.height,
                self.pos_x,
                self.pos_y,
                self.num_imgs,
                self.is_rgba << 7 | self.blocktype,
                self.align,
                self.compr,
                self.cent_y,
                self.cent_x,
            ),
        )

    def __bytes__(self):
        return self._bytes

    @staticmethod
    def loads(data: bytes):
        assert len(data) == BlockInfo.size
        (
            img_addr,
            picidx,
            sx,
            sy,
            pos_x,
            pos_y,
            parts,
            blocktype,
            align,
            compr,
            cent_y,
            cent_x,
        ) = BlockInfo._struct.unpack(data)
        is_rgba = blocktype & 0x80 != 0
        blocktype = BlockType(blocktype & 0x7F)
        align = BlockHorizontalAlignment(align)
        return BlockInfo(
            img_addr,
            picidx,
            sx,
            sy,
            pos_x,
            pos_y,
            parts,
            is_rgba,
            blocktype,
            align,
            compr,
            cent_x,
            cent_y,
        )


@dataclass
class WatchFaceMetaData:
    header: Header
    blocks_info: list[BlockInfo]
    imgs_size_info: list[int]

    def __post_init__(self):
        object.__setattr__(
            self,
            "_bytes",
            bytes(self.header)
            + b"".join([bytes(bi) for bi in self.blocks_info])
            + b"".join([int.to_bytes(sz, 4, "little") for sz in self.imgs_size_info]),
        )

    def __bytes__(self):
        return self._bytes

    @staticmethod
    def loads(data: bytes):
        header = Header.loads(data[: Header.size])
        block_info = [
            BlockInfo.loads(data[Header.size + i * BlockInfo.size : Header.size + (i + 1) * BlockInfo.size])
            for i in range(header.num_blocks)
        ]
        img_size_info = [
            int.from_bytes(
                data[
                    (Header.size + header.num_blocks * BlockInfo.size + i * 4) : (
                        Header.size + header.num_blocks * BlockInfo.size + (i + 1) * 4
                    )
                ],
                "little",
            )
            for i in range(header.num_img_info_size)
        ]
        return WatchFaceMetaData(header, block_info, img_size_info)


@dataclass
class ImageCompressedLineInfo:
    line_offset: int
    line_size: int
    size = 4

    def __post_init__(self):
        object.__setattr__(
            self,
            "_bytes",
            (self.line_offset | (self.line_size << 21)).to_bytes(4, "little"),
        )

    def __bytes__(self):
        return self._bytes

    @staticmethod
    def loads(data: bytes):
        assert len(data) == ImageCompressedLineInfo.size
        (data_int,) = struct.unpack("<I", data)
        line_offset = data_int & 0x001FFFFF
        line_size = (data_int & 0xFFE00000) >> 21
        return ImageCompressedLineInfo(line_offset, line_size)


@dataclass
class ImageCompressedData:
    lines_info: list[ImageCompressedLineInfo]
    compressed_data: bytes
    width: int
    height: int
    is_rgba: bool

    def __post_init__(self):
        object.__setattr__(self, "_bytes", self.compressed_data)

    def __bytes__(self):
        return self._bytes

    @staticmethod
    def loads(data: bytes, width: int, height: int, is_rgba: bool):
        lines_info_size = height * ImageCompressedLineInfo.size
        assert len(data) > lines_info_size
        lines_info = [
            ImageCompressedLineInfo.loads(
                data[i * ImageCompressedLineInfo.size : (i + 1) * ImageCompressedLineInfo.size]
            )
            for i in range(lines_info_size // ImageCompressedLineInfo.size)
        ]
        return ImageCompressedData(lines_info, data, width, height, is_rgba)

    def decompress(self) -> Image.Image:
        """
        Compression type is 0x04.
        Image is compressed using line-based run-length encoding (RLE).
        Image data starts with info for each line, containing the offset
        where the encoded line data lies, along with 1.5 bytes which
        currently have unknown purpose.

        The RLE is specified with prefix with the length of the repeating pixel
        values.
        There is possibility to specify "same" bit, which if cleared allows
        to continuously send N different pixel values.
        The prefix is 1 byte and has format: <same bit><7-bit length>.
        The pixel data has two types: one for RGBA image, and another for RGB
        images.
        RGBA pixel data is specified with 1 byte Alpha and 2 bytes RGB565
        encoded color data.
        RGB pixel data is specified with 2 bytes RGB565 data.

        Example:
            (RGBA) 8A 30 AB CD -> stop bit is one, which means the next byte
            will be prefix byte, alpha is 0x30, color is 0xABCD in RGB565.
            (RGB) 02 21 AB 22 CD -> stop bit is zero, which means there is no
            prefix byte after the pixel data for the current pixel.
            Instead, pixel data for the next pixels in the line are provided.
            As the count is 2, the pixel data for two consecutive pixels is
            provided. The first one has color 0x21AB, the next one 0x22CD.
        """

        def decompress_line(line, is_rgba):
            uncompressed_line = bytes()
            i = 0
            while i < len(line):
                prefix = line[i]
                same_val = prefix & 0x80
                n = prefix & 0x7F
                i += 1
                if same_val:
                    if is_rgba:
                        alpha = line[i]
                        rgb565 = (line[i + 1] << 8) | (line[i + 2])
                    else:
                        rgb565 = (line[i] << 8) | (line[i + 1])
                    red, green, blue = rgb565_to_rgb888(rgb565)
                    pixel_data = red.to_bytes(1, "little") + green.to_bytes(1, "little") + blue.to_bytes(1, "little")
                    if is_rgba:
                        pixel_data += alpha.to_bytes(1, "little")
                    uncompressed_line += n * pixel_data
                    i += 3 if is_rgba else 2
                else:
                    for _ in range(n):
                        if is_rgba:
                            alpha = line[i]
                            rgb565 = (line[i + 1] << 8) | (line[i + 2])
                        else:
                            rgb565 = (line[i] << 8) | (line[i + 1])
                        red, green, blue = rgb565_to_rgb888(rgb565)
                        pixel_data = (
                            red.to_bytes(1, "little") + green.to_bytes(1, "little") + blue.to_bytes(1, "little")
                        )
                        if is_rgba:
                            pixel_data += alpha.to_bytes(1, "little")
                        uncompressed_line += pixel_data
                        i += 3 if is_rgba else 2
            return uncompressed_line

        uncompressed_img_data = bytes()
        for line_info in self.lines_info:
            line_data = self.compressed_data[line_info.line_offset : line_info.line_offset + line_info.line_size]
            uncompressed_img_data += decompress_line(line_data, self.is_rgba)
        mode = "RGBA" if self.is_rgba else "RGB"
        return Image.frombytes(mode, (self.width, self.height), uncompressed_img_data)

    @staticmethod
    def compress(img: Image.Image):
        """
        Compression goes the other way around from the decompression.
        We process each line of the image and perform RLE.
        We keep track of the length of each compressed line, which also helps with
        calculating the line offset.
        """
        is_rgba = img.mode == "RGBA"
        width = img.width
        height = img.height
        pixels = img.load()

        def compress_line(line, is_rgba, width):
            # convert each line from RGB/RGBA to RGB565/ARGB565
            b_per_pix = 4 if is_rgba else 3

            if is_rgba:
                pix_vals = [
                    struct.Struct(">BH").pack(
                        line[b_per_pix * i + 3],
                        rgb888_to_rgb565(
                            line[b_per_pix * i + 0],
                            line[b_per_pix * i + 1],
                            line[b_per_pix * i + 2],
                        ),
                    )
                    for i in range(width)
                ]
            else:
                pix_vals = [
                    struct.Struct(">H").pack(
                        rgb888_to_rgb565(
                            line[b_per_pix * i + 0],
                            line[b_per_pix * i + 1],
                            line[b_per_pix * i + 2],
                        )
                    )
                    for i in range(width)
                ]
            compressed_line = bytes()
            count = 1
            same_val = False
            prev_val = pix_vals[0]
            segment_vals = prev_val
            b_per_val = 3 if is_rgba else 2
            for i_val, val in enumerate(pix_vals[1:]):
                if val == prev_val:
                    if not same_val:
                        if i_val > 0:
                            # store previous different values segment
                            segment_vals = segment_vals[:-b_per_val]
                            count -= 1
                            while count > 0:
                                subsegment_count = min(0x7F, count)
                                subsegment_vals = segment_vals[: subsegment_count * b_per_val]
                                prefix = subsegment_count
                                compressed_line += int.to_bytes(prefix, 1, "little") + subsegment_vals
                                segment_vals = segment_vals[subsegment_count * b_per_val :]
                                count -= subsegment_count
                            segment_vals = bytes()
                        count = 1
                        same_val = True
                    count += 1
                else:
                    if same_val:
                        # store previous same values segment
                        while count > 0:
                            subsegment_count = min(0x7F, count)
                            prefix = 0x80 | subsegment_count
                            pix_val = prev_val
                            compressed_line += int.to_bytes(prefix, 1, "little") + pix_val
                            count -= subsegment_count
                        count = 1
                        same_val = False
                        segment_vals = bytes()
                    else:
                        count += 1
                    segment_vals += val
                prev_val = val

            if same_val:
                while count > 0:
                    subsegment_count = min(0x7F, count)
                    prefix = 0x80 | subsegment_count
                    compressed_line += int.to_bytes(prefix, 1, "little") + prev_val
                    count -= subsegment_count
            else:
                while count > 0:
                    subsegment_count = min(0x7F, count)
                    prefix = subsegment_count
                    subsegment_vals = segment_vals[: subsegment_count * b_per_val]
                    compressed_line += int.to_bytes(prefix, 1, "little") + subsegment_vals
                    segment_vals = segment_vals[subsegment_count * b_per_val :]
                    count -= subsegment_count
            return compressed_line

        compressed_lines = []
        for i_line in range(height):
            line = b"".join(b"".join(int.to_bytes(p, 1, "little") for p in pixels[i, i_line]) for i in range(width))
            compr_line = compress_line(line, is_rgba, width)
            compressed_lines.append(compr_line)

        lines_info = []
        line_offset = ImageCompressedLineInfo.size * height
        for line in compressed_lines:
            lines_info.append(ImageCompressedLineInfo(line_offset, len(line)))
            line_offset += len(line)
        compressed_data = b"".join(bytes(li) for li in lines_info) + b"".join(compressed_lines)
        # pad compressed data to length of 4
        compressed_data += b"\x00" * (-len(compressed_data) % 4)
        return ImageCompressedData(lines_info, compressed_data, width, height, is_rgba)


@dataclass
class ImageData:
    data: bytes
    compression: int
    width: int
    height: int
    is_rgba: bool

    def __post_init__(self):
        object.__setattr__(self, "_bytes", self.data)

    def __bytes__(self):
        return self._bytes

    @staticmethod
    def loads(data: bytes, compression: int, width: int, height: int, is_rgba: bool):
        if compression != 0x00 and compression != 0x04:
            raise ValueError("Unsupported compression method")
        return ImageData(data, compression, width, height, is_rgba)

    def unpack(self) -> Image.Image:
        if self.compression == 0x00:
            mode = "RGBA" if self.is_rgba else "RGB"
            b_per_pix = 3 if self.is_rgba else 2
            # when compression is 0, data is stored RGB565 + optional Alpha
            # each line must have length multiple of 4, which means
            # each line may be padded if width is not multiple of 4
            line_length = self.width * b_per_pix
            pad_size = -line_length % 4
            line_length += pad_size
            num_lines = self.height
            pixels_data = b""
            for i_line in range(num_lines):
                line = self.data[i_line * line_length : (i_line + 1) * line_length - pad_size]
                if self.is_rgba:
                    pixels_data += b"".join(
                        struct.Struct("<BBBB").pack(
                            *rgb565_to_rgb888((line[i + 1] << 8) | (line[i + 2])),
                            line[i],
                        )
                        for i in range(0, len(line), b_per_pix)
                    )
                else:
                    pixels_data += b"".join(
                        struct.Struct("<BBB").pack(
                            *rgb565_to_rgb888((line[i] << 8) | (line[i + 1])),
                        )
                        for i in range(0, len(line), b_per_pix)
                    )
            return Image.frombytes(mode, (self.width, self.height), pixels_data)
        elif self.compression == 0x04:
            return ImageCompressedData.loads(self.data, self.width, self.height, self.is_rgba).decompress()

    @staticmethod
    def pack(img: Image.Image, compression: int):
        if compression != 0x00 and compression != 0x04:
            raise ValueError("Unsupported compression method")
        if compression == 0x00:
            width = img.width
            height = img.height
            is_rgba = img.mode == "RGBA"
            pixels = img.load()

            b_per_pix = 3 if is_rgba else 2
            line_length = width * b_per_pix
            pad_size = -line_length % 4
            line_length += pad_size
            num_lines = height
            pixels_data = b""
            for i_line in range(num_lines):
                if is_rgba:
                    line = b"".join(
                        struct.Struct(">BH").pack(
                            pixels[col, i_line][3],
                            rgb888_to_rgb565(
                                pixels[col, i_line][0],
                                pixels[col, i_line][1],
                                pixels[col, i_line][2],
                            ),
                        )
                        for col in range(width)
                    )
                else:
                    line = b"".join(
                        struct.Struct(">H").pack(
                            rgb888_to_rgb565(
                                pixels[col, i_line][0],
                                pixels[col, i_line][1],
                                pixels[col, i_line][2],
                            ),
                        )
                        for col in range(width)
                    )
                line += b"\x00" * pad_size
                pixels_data += line
            return ImageData(pixels_data, compression, width, height, is_rgba)
        elif compression == 0x04:
            return ImageCompressedData.compress(img)


@dataclass
class WatchFace:
    meta_data: WatchFaceMetaData
    imgs_data: list[ImageData]

    def __post_init__(self):
        object.__setattr__(
            self,
            "_bytes",
            bytes(self.meta_data) + b"".join(bytes(id) for id in self.imgs_data),
        )

    def __bytes__(self):
        return self._bytes

    @staticmethod
    def loads(data: bytes):
        meta_data = WatchFaceMetaData.loads(data)
        imgs_data = []
        for bi in meta_data.blocks_info:
            offset = bi.img_offset
            start_id = bi.img_id
            num_imgs = bi.num_imgs
            for img_id in range(start_id, start_id + num_imgs):
                img_size = meta_data.imgs_size_info[img_id]
                img_data = ImageData.loads(data[offset : offset + img_size], bi.compr, bi.width, bi.height, bi.is_rgba)
                imgs_data.append(img_data)
                offset += img_size
        return WatchFace(meta_data, imgs_data)

    def preview(
        self,
        width: int,
        height: int,
        hour: int = 9,
        minutes: int = 0,
        seconds: int = 23,
        date_year: int = 25,
        date_month: int = 25,
        date_day: int = 9,
        week_day: int = 3,
        steps: int = 23456,
        distance: float = 22.5,
        calories: int = 2345,
        heart_rate: int = 106,
        battery: int = 100,
    ) -> Image.Image | list[Image.Image]:
        def digital_block_paste(
            img: Image.Image, block_info: BlockInfo, value: float, num_digits: int, pad_zeros: bool = True
        ):
            value_str = str(value).zfill(num_digits) if pad_zeros else str(value)
            sign = -1 if block_info.align == BlockHorizontalAlignment.Right else 1
            start_x = (
                block_info.pos_x
                if block_info.align == BlockHorizontalAlignment.Left
                else block_info.pos_x - block_info.width
            )
            if sign == -1:
                value_str = value_str[::-1]
            for i, digit in enumerate(value_str):
                if digit == ".":
                    digit_id = 10
                else:
                    digit_id = int(digit)
                layer_img = self.imgs_data[block_info.img_id + digit_id].unpack()
                mask = layer_img if block_info.is_rgba else None
                img.paste(layer_img, (start_x + sign * i * block_info.width, block_info.pos_y), mask)

        def analog_block_paste(img: Image.Image, block_info: BlockInfo, angle: float, width: int, height: int):
            layer_img = self.imgs_data[block_info.img_id].unpack()
            new_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            center_x = block_info.width - block_info.cent_x
            center_y = block_info.height - block_info.cent_y
            x = block_info.pos_x - center_x
            y = block_info.pos_y - center_y
            mask = layer_img if block_info.is_rgba else None
            new_img.paste(layer_img, (x, y), mask)
            new_center_x = x + center_x
            new_center_y = y + center_y
            new_img = new_img.rotate(-angle, resample=Image.Resampling.BICUBIC, center=(new_center_x, new_center_y))
            new_mask = new_img if block_info.is_rgba else None
            img.paste(new_img, (0, 0), new_mask)

        animation_block = None
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        for bi in self.meta_data.blocks_info:
            if bi.blocktype == BlockType.Background:
                img.paste(self.imgs_data[bi.img_id].unpack(), (bi.pos_x, bi.pos_y))
            elif bi.blocktype == BlockType.Hours:
                digital_block_paste(img, bi, hour, 2)
            elif bi.blocktype == BlockType.Minutes:
                digital_block_paste(img, bi, minutes, 2)
            elif bi.blocktype == BlockType.Seconds:
                digital_block_paste(img, bi, seconds, 2)
            elif bi.blocktype == BlockType.HoursArm:
                angle = 30 * (hour % 12) + 30 * minutes / 60
                analog_block_paste(img, bi, angle, width, height)
            elif bi.blocktype == BlockType.MinutesArm:
                angle = 6 * minutes + 6 * seconds / 60
                analog_block_paste(img, bi, angle, width, height)
            elif bi.blocktype == BlockType.SecondsArm:
                angle = 6 * seconds
                analog_block_paste(img, bi, angle, width, height)
            elif bi.blocktype == BlockType.Year:
                digital_block_paste(img, bi, date_year, 2)
            elif bi.blocktype == BlockType.Month:
                digital_block_paste(img, bi, date_month, 2)
            elif bi.blocktype == BlockType.Day:
                digital_block_paste(img, bi, date_day, 2)
            elif bi.blocktype == BlockType.WeekDay:
                digital_block_paste(img, bi, week_day, 1)
            elif bi.blocktype == BlockType.Steps:
                digital_block_paste(img, bi, steps, 6, False)
            elif bi.blocktype == BlockType.Distance:
                digital_block_paste(img, bi, distance, 6, False)
            elif bi.blocktype == BlockType.DistanceLabel:
                img.paste(self.imgs_data[bi.img_id].unpack(), (bi.pos_x, bi.pos_y))
            elif bi.blocktype == BlockType.Calories:
                digital_block_paste(img, bi, calories, 4, False)
            elif bi.blocktype == BlockType.HeartRate:
                digital_block_paste(img, bi, heart_rate, 3, False)
            elif bi.blocktype == BlockType.Battery:
                battery_id = min(bi.num_imgs - 1, battery // (100 // bi.num_imgs))
                bat_img = self.imgs_data[bi.img_id + battery_id].unpack()
                img.paste(bat_img, (bi.pos_x, bi.pos_y), bat_img)
            elif bi.blocktype == BlockType.Animation:
                animation_block = bi
            else:
                print(f"Can't use block type {bi.blocktype} for preview")
        if animation_block:
            anim_layer_imgs = [
                self.imgs_data[animation_block.img_id + i].unpack() for i in range(animation_block.num_imgs)
            ]
            img = [img.copy() for _ in range(animation_block.num_imgs)]
            for i, anim_img in enumerate(anim_layer_imgs):
                img[i].paste(anim_img, (animation_block.pos_x, animation_block.pos_y), anim_img)
        return img


def get_arm_block_types():
    return [BlockType.HoursArm, BlockType.MinutesArm, BlockType.SecondsArm]


def get_origin_point(block_info: BlockInfo):
    origin_x = 0
    origin_y = 0
    if block_info.blocktype in get_arm_block_types():
        origin_x = block_info.width - block_info.cent_x
        origin_y = block_info.height - block_info.cent_y
    else:
        if block_info.align == BlockHorizontalAlignment.Center:
            origin_x = block_info.width // 2
        elif block_info.align == BlockHorizontalAlignment.Right:
            origin_x = block_info.width
    return origin_x, origin_y
