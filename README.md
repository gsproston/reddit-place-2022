# reddit-place-2022

Python scripts for processing data from Reddit's 2022 /r/place.

Datasets can be found from this Reddit post: https://www.reddit.com/r/place/comments/txvk2d/rplace_datasets_april_fools_2022/

## lastColouredPixel

Finds the location and datetime of the last pixel that was coloured before only white could be used.

## place2022.py

Generates the final canvas.

Uses the input files in `input/` and generates the final canvas as a png at `output/finalCanvas.png`

## splitFiles.py

Splits `input/2022_place_canvas_history.csv` into smaller CSV files, each 1,000,000 lines long.
