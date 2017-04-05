# TP3 Implementation IBM1 / Morard Damien

Algorithm which implements IBM Model 1
It has a parallel corpus of two langage for training
It returns a translation table and an alignement phrase
to phrase for a parallel corpus test

## Usage

```bash

python3 IBM1  [-h] [-n NUM_SENTENCE_TRAINING] [-i NUM_EM_ITERATION]
               [-t FOLDER_DATA_TRAINING] [-s FOLDER_DATA_TEST]

```

### Options

[-n] Specify number of sentence for training <br/>
[-i] Specify number of iteration for training <br/>
[-t] Folder for data training (name files are predefined as:
    "europarl_10k_es_en.es" and "europarl_10k_es_en.en"
    if you have different names change into IBM1.py
    with the variable sourceTrain and targetTrain) <br/>
[-s] Same as [-t] for data test <br/>

### Example

Output file can be seen in "outputAlign.txt" and "outputTranslation.txt"
