
find . -name "*.ipynb" -not -path "*/.ipynb_checkpoints/*" -exec jupyter nbconvert \
  --to notebook \
  --inplace \
  --ClearMetadataPreprocessor.enabled=True \
  --ClearMetadataPreprocessor.clear_notebook_metadata=False \
  --ClearMatadataPreprocessor.clear_cell_metadata=True  \
  --ClearMetadataPreprocessor.preserve_cell_metadata_mask='[("tags"),("scrolled")]' \
   {} \;