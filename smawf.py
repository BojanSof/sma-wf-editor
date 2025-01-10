import argparse
from dataclasses import dataclass
import struct
from PIL import Image


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class BlockInfo:
    img_offset: int
    img_id: int
    width: int
    height: int
    pos_x: int
    pos_y: int
    num_imgs: int
    blocktype: int
    align: int
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
                self.blocktype,
                self.align,
                self.compr,
                self.cent_x,
                self.cent_y,
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
            cent_x,
            cent_y,
        ) = BlockInfo._struct.unpack(data)
        return BlockInfo(
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
            cent_x,
            cent_y,
        )


@dataclass(frozen=True)
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
            BlockInfo.loads(
                data[
                    Header.size
                    + i * BlockInfo.size : Header.size
                    + (i + 1) * BlockInfo.size
                ]
            )
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


@dataclass(frozen=True)
class ImageLineInfo:
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
        assert len(data) == ImageLineInfo.size
        (data_int,) = struct.unpack("<I", data)
        line_offset = data_int & 0x001FFFFF
        line_size = (data_int & 0xFFE00000) >> 21
        return ImageLineInfo(line_offset, line_size)


@dataclass(frozen=True)
class ImageData:
    lines_info: list[ImageLineInfo]
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
        lines_info_size = height * ImageLineInfo.size
        assert len(data) > lines_info_size
        lines_info = [
            ImageLineInfo.loads(
                data[i * ImageLineInfo.size : (i + 1) * ImageLineInfo.size]
            )
            for i in range(lines_info_size // ImageLineInfo.size)
        ]
        return ImageData(lines_info, data, width, height, is_rgba)

    def decompress(self) -> Image.Image:
        """
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
            def rgb565_to_rgb888(rgb565: int) -> tuple[int, int, int]:
                red = ((rgb565 >> 11) * 255 + 15) // 31
                green = (((rgb565 >> 5) & 0x3F) * 255 + 31) // 63
                blue = ((rgb565 & 0x1F) * 255 + 15) // 31
                return (red, green, blue)

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
                    pixel_data = (
                        red.to_bytes(1, "little")
                        + green.to_bytes(1, "little")
                        + blue.to_bytes(1, "little")
                    )
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
                            red.to_bytes(1, "little")
                            + green.to_bytes(1, "little")
                            + blue.to_bytes(1, "little")
                        )
                        if is_rgba:
                            pixel_data += alpha.to_bytes(1, "little")
                        uncompressed_line += pixel_data
                        i += 3 if is_rgba else 2
            return uncompressed_line

        uncompressed_img_data = bytes()
        for line_info in self.lines_info:
            line_data = self.compressed_data[
                line_info.line_offset : line_info.line_offset + line_info.line_size
            ]
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
            def rgb888_to_rgb565(r: int, g: int, b: int) -> int:
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                return rgb565

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
                                subsegment_vals = segment_vals[
                                    : subsegment_count * b_per_val
                                ]
                                prefix = subsegment_count
                                compressed_line += (
                                    int.to_bytes(prefix, 1, "little") + subsegment_vals
                                )
                                segment_vals = segment_vals[
                                    subsegment_count * b_per_val :
                                ]
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
                            compressed_line += (
                                int.to_bytes(prefix, 1, "little") + pix_val
                            )
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
                    compressed_line += (
                        int.to_bytes(prefix, 1, "little") + subsegment_vals
                    )
                    segment_vals = segment_vals[subsegment_count * b_per_val :]
                    count -= subsegment_count
            return compressed_line

        compressed_lines = []
        for i_line in range(height):
            line = b"".join(
                b"".join(int.to_bytes(p, 1, "little") for p in pixels[i, i_line])
                for i in range(width)
            )
            compr_line = compress_line(line, is_rgba, width)
            compressed_lines.append(compr_line)

        lines_info = []
        line_offset = ImageLineInfo.size * height
        for line in compressed_lines:
            lines_info.append(ImageLineInfo(line_offset, len(line)))
            line_offset += len(line)
        compressed_data = b"".join(bytes(li) for li in lines_info) + b"".join(
            compressed_lines
        )
        return ImageData(lines_info, compressed_data, width, height, is_rgba)


@dataclass(frozen=True)
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
                img_data = ImageData.loads(
                    data[offset : offset + img_size],
                    bi.width,
                    bi.height,
                    bi.blocktype & 0x80 != 0,
                )
                imgs_data.append(img_data)
                offset += img_size
        return WatchFace(meta_data, imgs_data)
