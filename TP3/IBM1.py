#! /usr/bin/env python3

from itertools import chain
import time
import operator
import argparse


def returnSentences(sourceFile, targetFile, nbMaxSentence):
    # Retourne un nombre de phrases choisies par rapport
    # aux 50 000 phrases du fichier original
    # Nous avons ainsi le même nombre de phrases source
    # et target mais réduit
    sourceSentences = []
    targetSentences = []
    nbCurrentSentence = 0

    with open(sourceFile) as sFile, open(targetFile) as tFile:
        for sentence in sFile:
            if nbCurrentSentence < nbMaxSentence:
                sourceSentences.append(sentence.split())
            nbCurrentSentence += 1
        nbCurrentSentence = 0
        for sentence in tFile:
            if nbCurrentSentence < nbMaxSentence:
                targetSentences.append(sentence.split())
            nbCurrentSentence += 1

    return (sourceSentences, targetSentences)


def train(sourceFile, targetFile, nbIte, nbMaxSentence):
    # Initialisation uniforme de la probabilité t(e|f)
    # e étant le target file et f le source file
    t = {}
    nbWords = 0
    sourceSentences = []
    targetSentences = []
    i = 0

    # On commence par initialiser nos valeurs uniformement
    # On en profite aussi pour enregistrer toutes les phrases
    # dans deux listes pour ne pas avoir à re-parcourir les fichiers

    (sourceSentences, targetSentences) = returnSentences(
        sourceFile, targetFile, nbMaxSentence)

    # Vu que nous avons des listes de listes nous applatissons le tout
    # pour avoir une seule liste et compter le nombre de mots
    listWords = list(chain(*sourceSentences))
    nbWords = len(listWords)
    initValue = 1 / nbWords

    for sSentence, tSentence in zip(sourceSentences, targetSentences):
        sSplit = sSentence
        tSplit = tSentence
        for tWords in tSplit:
            for sWords in sSplit:
                if (tWords, sWords) not in t:
                    t[tWords, sWords] = initValue
    print('Algorithme EM en cours:')
    # Boucle EM
    while i < nbIte:
        count = {}
        total = {}
        sTot = {}
        i += 1
        print('Itération numéro {}'.format(i))
        for sSentence, tSentence in zip(sourceSentences, targetSentences):
            for tWords in tSentence:
                sTot[tWords] = 0
                for sWords in sSentence:
                    sTot[tWords] += t[tWords, sWords]
            for tWords in tSentence:
                for sWords in sSentence:
                    if (tWords, sWords) not in count:
                        count[tWords, sWords] = t[tWords,
                                                  sWords] / sTot[tWords]
                    else:
                        count[tWords, sWords] += t[tWords,
                                                   sWords] / sTot[tWords]
                    if sWords not in total:
                        total[sWords] = t[tWords, sWords] / sTot[tWords]
                    else:
                        total[sWords] += t[tWords, sWords] / sTot[tWords]

        for (tWords, sWords) in count.keys():
            t[tWords, sWords] = count[tWords, sWords] / total[sWords]

    return t


def align(t, sourceFile, targetFile, nbMaxSentence):

    sourceSentences = []
    targetSentences = []
    (sourceSentences, targetSentences) = returnSentences(
        sourceFile, targetFile, nbMaxSentence)

    alignement = []
    sentenceAlign = []
    probMax = 0
    pos = (-1, -1)

    # Pour aligner nous prenons les phrases pair à pair
    # Puis nous parcourons tous les mots un à un pour voir
    # quel est la traduction avec la plus grande probabilité
    # On stock le tout dans un tableau qui pour chaque phrase
    # contient un tableau avec des tuples qui donne la position
    # du mot de la phrase source et de la phrase target
    for sSentence, tSentence in zip(sourceSentences, targetSentences):
        for i, tWords in enumerate(tSentence):
            for j, sWords in enumerate(sSentence):
                if (tWords, sWords) not in t:
                    probTemp = 0
                else:
                    probTemp = t[tWords, sWords]
                if probTemp > probMax:
                    probMax = probTemp
                    pos = (j, i)
            sentenceAlign.append(pos)
            probMax = 0
            # L'initialisation -1,-1 sert à observer si on a aucune traduction
            # en sortie
            pos = (-1, -1)
        alignement.append(sentenceAlign)
        sentenceAlign = []

    return alignement


def score(guessFile, goldFile):

    nbGuess = 0
    nbCorrect = 0
    nbAnswer = 0

    with open(guessFile) as guFile, open(goldFile) as goFile:
        for guess, gold in zip(guFile, goFile):
            guessSplit = guess.split()
            goldSplit = gold.split()
            nbGuess += len(guessSplit)
            nbAnswer += len(goldSplit)
            nbCorrect += len(set(guessSplit).intersection(goldSplit))

            precision = nbCorrect / nbGuess
            recall = nbCorrect / nbAnswer
            scoreF1 = 2 * precision * recall / (precision + recall)

    return (precision, recall, scoreF1)


def write_translations(t, outputFile, nbMaxPair):
    # Vu le nombre gigantesque de pair dans la table de translation t
    # on en affiche un nombre max
    i = 0
    with open(outputFile, 'w') as outFile:
        for pair in sorted(t.items(), key=operator.itemgetter(1), reverse=True):
            if i < nbMaxPair:
                output = '{} {} {} \n'.format(pair[0][0], pair[0][1], pair[1])
                outFile.write("{}".format(output))
            i += 1


def write_alignements(alignements, outputFile):

    with open(outputFile, 'w') as outFile:
        for alignement in alignements:
            for pos in alignement:
                output = '{}-{}'.format(pos[0], pos[1])
                outFile.write("{} ".format(output))
            outFile.write('\n')


if __name__ == '__main__':

    time1 = time.clock()

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", dest="num_sentence_training",
                        default=10000, type=int, help="Number of sentence for training (default: 10000)")
    parser.add_argument("-i", dest="num_EM_iteration",
                        default=5, type=int, help="Number of EM iterations (default: 5)")
    parser.add_argument("-t", dest="folder_data_training",
                        default='data/training', type=str, help="Destination of the folder which contains data training (default: data/training)")
    parser.add_argument("-s", dest="folder_data_test",
                        default='data/test', type=str, help="Destination of the folder which contains data test (default: data/test)")
    args = parser.parse_args()

    nbMaxSentenceTraining = args.num_sentence_training
    nbIte = args.num_EM_iteration
    sourceTrain = "{}/europarl_50k_es_en.es".format(args.folder_data_training)
    targetTrain = "{}/europarl_50k_es_en.en".format(args.folder_data_training)
    sourceTest = "{}/test.es".format(args.folder_data_test)
    targetTest = "{}/test.en".format(args.folder_data_test)

    outputAlign = 'outputAlign.txt'
    outputTranslation = 'outputTranslation.txt'

    nbMaxSentenceTest = 100
    nbMaxPair = 20

    t = train(sourceTrain, targetTrain, nbIte, nbMaxSentenceTraining)
    alignements = align(t, sourceTest, targetTest, nbMaxSentenceTest)
    write_alignements(alignements, outputAlign)
    write_translations(t, outputTranslation, nbMaxPair)

    time2 = time.clock()
    finalTime = time2 - time1
    print(
        "Le programme a mis {:.2f} secondes pour s'exécuter".format(finalTime))

    (precision, recall, scoreF1) = score(outputAlign, 'data/test/test.align')
    print("La précision est de: {:.3f}".format(precision))
    print("Le recall est de: {:.3f}".format(recall))
    print("Le score F1 est de: {:.3f}".format(scoreF1))
