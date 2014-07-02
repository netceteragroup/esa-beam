#!/bin/bash

LIBRAT_SCENES="$@"

# LIBRAT_SCENES="${HOME}/.beam/beam-vlab/auxdata/librat_scenes/"

if which parallel
then
    find "$LIBRAT_SCENES" -regex ".*\\.\\(obj\\(\\.crown\\)?\\|dem\\)"         \
         -exec parallel --progress --eta                                       \
         ./preprocess_obj_file.sh ::: {} +
else
    find "$LIBRAT_SCENES" -regex ".*\\.\\(obj\\(\\.crown\\)?\\|dem\\)"         \
         -exec ./preprocess_obj_file.sh {} \;
fi
