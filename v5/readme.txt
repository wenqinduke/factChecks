##File structure:

**databaseOpt.py**: create a database for word to question id mapping.

**test_question.py**: create a databse for test questions; select potential matching ids (potential_id) for each question.

**checkIdList.py**: Check whether potential_id list captures all the corresponding facts id for each question.

**Test_mass_adaboost.py**: the entry point of this algorithm. We have 111 questions and corresponding facts available for training and testing. In this file, you can specify which test questions are for training and the rest for testing by defining test_id_region.

**main.py**: For each question, generate data arrays with all potential facts; return a list of matching facts.

**match.py**: The bi-partite matching algorithm; returns a list of features between one question and one fact.

**dataset.py**: Constructs the training set.


**check_wrong_match.py**: Check false positives and false negatives by comparing test results and actual corresponding facts. Also calculate precision and recall.

**analyse_adaboost_*_txt**: There are nine txt files (starts with analyse_adaboost), which are the test results using different training set along with different train/test split.

##To run:
1.  Download GoogleNews-vectors-negative300.bin and put it under Model/ (parallel to v5)

2.  Make sure that database is set up. If you have
