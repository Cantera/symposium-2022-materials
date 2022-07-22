
find . -name "*.ipynb" -exec jupyter nbconvert \
  --to notebook \
  --execute \
  --inplace \
  --ClearMetadataPreprocessor.enabled=True \
  --ClearMetadataPreprocessor.clear_notebook_metadata=False \
  --ClearMatadataPreprocessor.clear_cell_metadata=True  \
  --ClearMetadataPreprocessor.preserve_cell_metadata_mask='[("tags"),("scrolled")]' \
   {} \;