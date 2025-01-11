import argparse
import pathlib
import sys
from smawf import WatchFace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SMA smart watches face decompressor",
        description="Decompress the image resources from SMA smart watches watch face files",
    )
    parser.add_argument("-i", "--input_file", type=pathlib.Path, required=True)
    parser.add_argument("-o", "--output_dir", type=pathlib.Path)
    args = parser.parse_args()
    if not args.input_file.exists():
        print(f"Input file `{args.input_file}` does not exist")
        sys.exit(-1)
    output_dir = (
        args.output_dir if args.output_dir else pathlib.Path(args.input_file.stem)
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.input_file, "rb") as f:
        wf_data = f.read()
    wf = WatchFace.loads(wf_data)
    for i, img_data in enumerate(wf.imgs_data):
        print("Extracting image {i:03d}.png")
        img = img_data.decompress()
        img.save(output_dir / f"{i:03d}.png")
