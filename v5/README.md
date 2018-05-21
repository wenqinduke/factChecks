
#File structure:
**pre_process_sentence.py**: Pre-process the sentence and words by remote stop words, lemmatize words, get rid of punctuations, get tags and entities for words, etc,.

**summary.py**: For each fact, get the summary sentence from its URL.

**databaseOpt.py**: create a database for word to question id mapping.

**test_question.py**: create a databse for test questions; select potential matching ids (potential_id) for each question.

**checkIdList.py**: Check whether potential_id list captures all the corresponding facts id for each question.

**Test_mass_adaboost.py**: the entry point of this algorithm. We have 111 questions and corresponding facts available for training and testing. In this file, you can specify which test questions are for training and the rest for testing by defining test_id_region.

**main.py**: For each question, generate data arrays with all potential facts; return a list of matching facts.

**match.py**: The bi-partite matching algorithm; returns a list of features between one question and one fact.

**ml.py**: This class is used to do machine learning but it is no longer used anymore. Right now the only method used is ml.get_data_array, which collects the data from database and form it as an array. (further developer might move this method into other class and delete this python file.)

**dataset.py**: Constructs the training set.

**check_wrong_match.py**: Check false positives and false negatives by comparing test results and actual corresponding facts. Also calculate precision and recall.

**analyse_adaboost_*_txt**: There are nine txt files (starts with analyse_adaboost), which are the test results using different training set along with different train/test split.

#To run: (with already generated training sets)
1.  Download GoogleNews-vectors-negative300.bin and put it under Model/ (parallel to v5)

2.  unzip sharefacts_v5.sql.zip then dump the database file: psql sharefacts < database/sharefacts_v5.sql

3.  Choose which training set you want to run, and specify the test cases in test_mass_adaboost.py.

4. python test_mass_adaboost.py
