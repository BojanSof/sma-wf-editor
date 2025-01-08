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

        def rgb565_to_rgb888(rgb565: int) -> tuple[int, int, int]:
            red = ((rgb565 >> 11) * 255 + 15) // 31
            green = (((rgb565 >> 5) & 0x3F) * 255 + 31) // 63
            blue = ((rgb565 & 0x1F) * 255 + 15) // 31
            return (red, green, blue)

        uncompressed_img_data = bytes()
        for line_info in self.lines_info:
            line_data = self.compressed_data[
                line_info.line_offset : line_info.line_offset + line_info.line_size
            ]
            i = 0
            while i < len(line_data):
                prefix = line_data[i]
                same_val = prefix & 0x80
                n = prefix & 0x7F
                i += 1
                if same_val:
                    if self.is_rgba:
                        alpha = line_data[i]
                        rgb565 = (line_data[i + 1] << 8) | (line_data[i + 2])
                    else:
                        rgb565 = (line_data[i] << 8) | (line_data[i + 1])
                    red, green, blue = rgb565_to_rgb888(rgb565)
                    pixel_data = (
                        red.to_bytes(1, "little")
                        + green.to_bytes(1, "little")
                        + blue.to_bytes(1, "little")
                    )
                    if self.is_rgba:
                        pixel_data += alpha.to_bytes(1, "little")
                    uncompressed_img_data += n * pixel_data
                    i += 3 if self.is_rgba else 2
                else:
                    for _ in range(n):
                        if self.is_rgba:
                            alpha = line_data[i]
                            rgb565 = (line_data[i + 1] << 8) | (line_data[i + 2])
                        else:
                            rgb565 = (line_data[i] << 8) | (line_data[i + 1])
                        red, green, blue = rgb565_to_rgb888(rgb565)
                        pixel_data = (
                            red.to_bytes(1, "little")
                            + green.to_bytes(1, "little")
                            + blue.to_bytes(1, "little")
                        )
                        if self.is_rgba:
                            pixel_data += alpha.to_bytes(1, "little")
                        uncompressed_img_data += pixel_data
                        i += 3 if self.is_rgba else 2
        mode = "RGBA" if self.is_rgba else "RGB"
        return Image.frombytes(mode, (self.width, self.height), uncompressed_img_data)


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
