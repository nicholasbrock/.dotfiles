#!/usr/bin/env python3
"""
Module documentation goes here
"""


import argparse
import subprocess
import sys
from xml.etree import ElementTree


def parse_output(output, test):
    """Method documentation goes here.
    """
    error_msg = "ERROR: {} EXPECTED: {}, ACTUAL: {}\n"
    # try parsing output
    root = None
    try:
        root = ElementTree.fromstring(output)
    except ElementTree.ParseError as parse_error:
        return (error_msg.format("XML Parse Error", "Valid XML Tree", parse_error)
            + "\n\tAborting Test...")

    if not test:
        return ""

    return_msg = ""
    # check semester
    if root.tag != "semester":
        return_msg = error_msg.format("Semester Tag", "semester", root.tag)

    if root.attrib['id'] != test['semester']:
        return_msg += error_msg.format("Semester ID",
                                      test['semester'],
                                      root.attrib['id'])

    # check number of students
    if len(root) != len(test['students']):
        return_msg += error_msg.format("Student Count",
                                       len(root),
                                       len(test['students']))
        return return_msg

    student_index = 0
    for student in root:
        if student.tag != "student":
            return_msg += error_msg.format("Student Tag",
                                           "student",
                                           student.tag)

        if student.attrib['id'] != test['students'][student_index]['stu_id']:
            return_msg += error_msg.format(
                "Student ID",
                test['students'][student_index]['stu_id'],
                student.attrib['id']
            )

        for grade_unit in student:
            if grade_unit.tag == "exams":
                exam_dict = test['students'][student_index]['exams']
                if len(grade_unit) != len(exam_dict):
                    return_msg += error_msg.format(
                        f"Student {student.attrib['id']} Exam Count",
                        len(exam_dict)),
                        len(grade_unit)
                    return_msg += '\n'
                    continue

                for exam in grade_unit:
                    # check tag name
                    if exam.tag != "exam":
                        return_msg += error_msg.format(
                            "Exam tag name",
                            "exam",
                            exam.tag
                        )
                    # find exam by id
                    if exam.attrib['id'] not in exam_dict:
                        return_msg += error_msg.format(
                            f"Student {student.attrib['id']} Missing Exam",
                            f"{exam.attrib['id']} in {list(exam_dict.keys())}",
                            "not found"
                        )
                        continue
                    # check exam text
                    if exam.text != exam_dict[exam.attrib['id']]:
                        return_msg += error_msg.format(
                            f"Student {student.attrib['id']} Exam {exam.attrib['id']}",
                            exam_dict[exam.attrib['id']]),
                            exam.text

            elif grade_unit.tag == "quizzes":
                quiz_dict = test['students'][student_index]['quizzes']
                if len(grade_unit) != len(quiz_dict):
                    return_msg += error_msg.format(
                        f"Student {student.attrib['id']} Quiz Count",
                        len(quiz_dict)),
                        len(grade_unit)
                    return_msg += '\n'
                    continue

                for quiz in grade_unit:
                    # check tag name
                    if quiz.tag != "quiz":
                        return_msg += error_msg.format(
                            "Quiz tag name",
                            "quiz",
                            quiz.tag
                        )
                    # find quiz by id
                    if quiz.attrib['id'] not in quiz_dict:
                        return_msg += error_msg.format(
                            f"Student {student.attrib['id']} Missing Quiz",
                            f"{quiz.attrib['id']} in {list(quiz_dict.keys())}",
                            "not found"
                        )
                        continue
                    # check quiz text
                    if quiz.text != quiz_dict[quiz.attrib['id']]:
                        return_msg += error_msg.format(
                            f"Student {student.attrib['id']} Quiz {quiz.attrib['id']}",
                            quiz_dict[quiz.attrib['id']]),
                            quiz.text
            else:
                return_msg += error_msg.format(
                    "Grade Units",
                    f"{grade_unit.tag} in [\"exams\", \"quizzes\"]",
                    "not found"
                )
        student_index += 1

    return return_msg


TEST_1 = {
    "semester" : "23sp",
    "students" : [{
        "stu_id" : "00001",
        "exams" : {"1" : "87", "2" : "79", "3" : "73"},
        "quizzes" : {"1" : "3.7", "3" : "4.0"}
    }, {
        "stu_id" : "00002",
        "exams" : {"1" : "98", "2" : "81", "3" : "76"},
        "quizzes" : {"1" : "4.0", "2" : "3.8", "3" : "3.5"}
    }]
}

TEST_2 = {
    "semester" : "23su",
    "students" : [{
        "stu_id" : "00001",
        "exams" : {"1" : "87", "2" : "79", "3" : "73"},
        "quizzes" : {"1" : "3.7", "2" : "4.0"}
    }, {
        "stu_id" : "00002",
        "exams" : {"1" : "98", "2" : "81", "3" : "76"},
        "quizzes" : {"1" : "4.0", "2" : "3.8", "3" : "3.5"}
    }, {
        "stu_id" : "00003",
        "exams" : {"1" : "100", "2" : "99", "3" : "105"},
        "quizzes" : { }
    }]
}

TEST_3 = {
    "semester" : "23su",
    "students" : [{
        "stu_id" : "00001",
        "exams" : {"1" : "87", "2" : "79", "3" : "73"},
        "quizzes" : {"1" : "3.7", "2" : "4.0"}
    }, {
        "stu_id" : "00002",
        "exams" : {"1" : "98", "2" : "81", "3" : "76"},
        "quizzes" : {"1" : "4.0", "2" : "3.8", "3" : "3.5"}
    }, {
        "stu_id" : "00005",
        "exams" : { },
        "quizzes" : {"1" : "4.0", "2" : "3.8", "3" : "3.5"}
    }]
}

TEST_4 = {
    "semester" : "24sp",
    "students" : [{
        "stu_id" : "00001",
        "exams" : {"1" : "87", "2" : "79", "3" : "73"},
        "quizzes" : {"1" : "3.7", "2" : "4.0"}
    }, {
        "stu_id" : "00002",
        "exams" : {"1" : "98", "2" : "81", "3" : "76"},
        "quizzes" : {"1" : "4.0", "2" : "3.8", "3" : "3.5"}
    }, {
        "stu_id" : "00003",
        "exams" : {"1" : "100", "2" : "99", "3" : "105"},
        "quizzes" : { }
    }, {
        "stu_id" : "00005",
        "exams" : { },
        "quizzes" : {"1" : "3.99", "2" : "3.85", "3" : "3.5"}
    }, {
        "stu_id" : "00004",
        "exams" : { },
        "quizzes" : { }
    }]
}


class QuickTest:
    """Class documentation goes here
    """
    def __init__(self, test):
        self._exe = ["./parse-grades"]
        self._timeout = 5

        self._test_file = "grades_1.txt"
        self._test_data = None
        if test == 1:
          self._test_data = TEST_1
        elif test == 2:
          self._test_file = "grades_2.txt"
          self._test_data = TEST_2
        elif test == 3:
          self._test_file = "grades_3.txt"
          self._test_data = TEST_3
        elif test == 4:
          self._test_file = "grades_4.txt"
          self._test_data = TEST_4



    def test(self):
        """Method documentation goes here
        """
        file_text = ""
        with open(self._test_file, 'r') as file_in:
            file_text = file_in.read()

        returncode, stdout = self.run(file_text)

        if returncode != 0:
            print(
                f"ERROR: EXPECTED return 0, ACTUAL return {returncode}.",
                file=sys.stderr)

        if not stdout:
            print("ERROR: No output from student app.", file=sys.stderr)
            sys.exit(1)

        print("BEGIN STUDENT OUTPUT")
        print("------------------------")
        print(stdout.strip())
        print("------------------------")
        print("END STUDENT OUTPUT")

        result = parse_output(stdout, self._test_data)
        if result:
          print(result)
          print("TEST FAILED")
          return False
        print("TEST PASSED")
        return True


    def run(self, text_in):
        """Method documentation goes here.
        """
        try:
            result = subprocess.run(args=self._exe,
                                    input=text_in,
                                    universal_newlines=True,  # open IO in text mode
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    timeout=self._timeout,
                                    check=False)
            return result.returncode, result.stdout

        except subprocess.TimeoutExpired:
            print("Timeout expired")
            return 10, None, f"Execution timed out after {self._timeout}s\n"

        except subprocess.CalledProcessError as proc_err:
            print(proc_err)
            return 1, None, f"Exited with code {proc_err.returncode}\n"


if __name__ == "__main__":
    CL_PARSER = argparse.ArgumentParser(
        prog='test_parse_grades.py',
        description="Executes one of three tests on executable parse-grades")
    CL_PARSER.add_argument('test', metavar="TEST_NUMBER", type=int,
                           choices={0, 1, 2, 3, 4},
                           help="Test number from {0, 1, 2, 3, 4}")
    ARGS = CL_PARSER.parse_args()

    TEST = QuickTest(ARGS.test)
    if TEST.test():
      exit(0)
    exit(1)
