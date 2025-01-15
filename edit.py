import argparse
import os
import pathlib
import sys

from PIL import Image

from smawf import WatchFace, ImageData, BlockInfo, WatchFaceMetaData

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SMA smart watches face edit script",
        description="Compress the edited image resources and edit the given watch face file",
    )
    parser.add_argument("-i", "--input_file", type=pathlib.Path, required=True)
    parser.add_argument("-r", "--input_image_dir", type=pathlib.Path, required=True)
    parser.add_argument("-o", "--output_file", type=pathlib.Path)
    args = parser.parse_args()
    if not args.input_file.exists():
        print(f"Input file `{args.input_file}` does not exist")
        sys.exit(-1)
    if not args.input_image_dir.exists():
        print(f"Input image directory `{args.input_image_dir}` does not exist")
        sys.exit(-2)
    with open(args.input_file, "rb") as f:
        wf_data = f.read()
    wf = WatchFace.loads(wf_data)
    # compress the image resources
    imgs_data = []
    for img_name in sorted(os.listdir(args.input_image_dir)):
        img = Image.open(os.path.join(args.input_image_dir, img_name))
        print(f"Processing {img_name}")
        img_data = ImageData.pack(img, 0x04)
        imgs_data.append(img_data)
    # update meta data
    print("Adjusting watch face meta data")
    # update image size info table
    imgs_size_info = [len(bytes(img_data)) for img_data in imgs_data]
    # update imgs offsets in blocks
    img_offset = wf.meta_data.blocks_info[0].img_offset
    blocks_info = []
    for bi in wf.meta_data.blocks_info:
        block_info = BlockInfo(
            img_offset=img_offset,
            img_id=bi.img_id,
            width=bi.width,
            height=bi.height,
            pos_x=bi.pos_x,
            pos_y=bi.pos_y,
            num_imgs=bi.num_imgs,
            blocktype=bi.blocktype,
            align=bi.align,
            compr=bi.compr,
            cent_x=bi.cent_x,
            cent_y=bi.cent_y,
        )
        blocks_info.append(block_info)
        for i in range(bi.num_imgs):
            img_offset += imgs_size_info[bi.img_id + i]
    print("Saving new watch face file")
    new_wf = WatchFace(
        WatchFaceMetaData(wf.meta_data.header, blocks_info, imgs_size_info), imgs_data
    )
    with open(args.output_file, "wb") as f:
        f.write(bytes(new_wf))
