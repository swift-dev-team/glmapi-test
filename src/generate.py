import unittest
import requests as r
import os.path as path
import os
import time
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HOST=os.getenv("HOST")
BUSINESS_ID="41315905-e402-4eae-bb2f-df20e2d11a86"
PWD=Path(path.abspath("./"))

def print_response_body(response):
    print("\033[93m" + response.text + "\033[0m")

def file_list(folder="input/2"):
    INPUT_DIR=PWD / "data" / folder
    map_result = map(lambda x: (INPUT_DIR / x, x),
        filter(lambda x: x[0] != "_", os.listdir(INPUT_DIR))
    )
    return list(map_result)

def purify_content(content):
    return '"' + content.replace("\n", "⏎").replace("\r", "⏎").replace("\t", "⇥") + '"'

def log(filename, val):
    OUTPUT_DIR=PWD/"data"/"output"/"2"
    if not path.exists(OUTPUT_DIR):
        Path.mkdir(OUTPUT_DIR, parents=True, exist_ok=True)
    with open(OUTPUT_DIR/filename, "a") as file:
        file.write(val + "\n")

class TestGenerateAction(unittest.TestCase):
    URL=f"{HOST}/v1/generate"

    def __init__(self, *args, **kwargs):
        super(TestGenerateAction, self).__init__(*args, **kwargs)
        self.__fill_vector_data()

    def __get_vector_ids(self):
        url = f"{HOST}/v1/vs/{BUSINESS_ID}"
        response = r.get(url)
        return response

    def __has_vector_data(self):
        response = self.__get_vector_ids()
        return response.status_code == 200 and len(response.json()["result"]) > 0

    def __fill_vector_data(self):
        if self.__has_vector_data():
            return
        file1 = PWD / "data" / "input" / "1" / "1.basic_info.txt"
        file2 = PWD / "data" / "input" / "1" / "2.产品信息202305242.xlsx"
        url = f"{HOST}/v1/vs"
        with open(file1, "rb") as file:
            r.post(
                url,
                files={
                    "file": (path.basename(file1), file, "text/plain")
                },
                data={
                    "business_id": BUSINESS_ID,
                    "metadata": '{"name": "1.basic_info.txt"}'
                }
            )
        with open(file2, "rb") as file:
            r.post(
                url,
                files={
                    "file": (path.basename(file1), file, "text/plain")
                },
                data={
                    "business_id": BUSINESS_ID,
                    "metadata": '{"name": "2.产品信息202305242.xlsx"}'
                }
            )
        return

    def __get_result(self, job_id):
        url = f"{HOST}/v1/result/{job_id}"
        response = r.get(url)
        return response

    def test_1_business_email(self):
        log_filename = time.strftime("%Y-%m-%d %H:%M:%S") + " business_email.csv"
        log(log_filename, "id,output")
        response = r.post(
            self.URL,
            json={
                "business_id": BUSINESS_ID,
                "model": "email-generate",
                "content": {}
            }
        )
        print_response_body(response)
        self.assertIn(response.status_code, [200, 201])
        self.assertEqual(response.json()["status"], "CREATED")
        job_id = response.json()["job_id"]
        cnt = 0
        while(True):
            cnt = cnt + 1
            time.sleep(10)
            response = self.__get_result(job_id)
            print_response_body(response)
            self.assertIn(response.status_code, [200, 201])
            self.assertIn(response.json()["status"], ["OK", "WAITING", "PROCESSING"])
            if response.json()["status"] == "OK":
                log(log_filename, f"{job_id},{purify_content(response.json()['result'])}")
                break

    def test_2_email_summary(self):
        log_filename = time.strftime("%Y-%m-%d %H:%M:%S") + " email_summary.csv"
        log(log_filename, "file_name,input,output")
        job_list = set()
        for pp in file_list():
            with open(pp[0], "r") as file:
                content = file.read()
                response = r.post(
                    self.URL,
                    json={
                        "model": "email",
                        "content": {
                            "email": content
                        }
                    }
                )
                print_response_body(response)
                self.assertIn(response.status_code, [200, 201])
                self.assertEqual(response.json()["status"], "CREATED")
                job_list.add(
                    (response.json()["job_id"], pp[1], content)
                )

        while job_list:
            entity = job_list.pop()
            time.sleep(10)
            response = self.__get_result(entity[0])
            print_response_body(response)
            self.assertIn(response.status_code, [200, 201])
            self.assertIn(response.json()["status"], ["OK", "WAITING", "PROCESSING"])
            if response.json()["status"] == "OK":
                log(log_filename, f"{entity[1]},{purify_content(entity[2])},{purify_content(response.json()['result'])}")
                continue
            job_list.add(entity)

    def test_3_reply_summary(self):
        log_filename = time.strftime("%Y-%m-%d %H:%M:%S") + " reply_summary.csv"
        log(log_filename, "file_name,input,output")
        job_list = set()

        def tmp_result(content, name):
            TMP_DIR=PWD/"data"/"tmp"
            if not path.exists(TMP_DIR):
                Path.mkdir(TMP_DIR, parents=True, exist_ok=True)
            with open(TMP_DIR/name, "w") as file:
                file.write(content)

        for pp in file_list():
            with open(pp[0], "r") as file:
                content = file.read()
                response = r.post(
                    self.URL,
                    json={
                        "model": "summ",
                        "content": {
                            "summ": content
                        },
                        "business_id": BUSINESS_ID
                    }
                )
                print_response_body(response)
                self.assertIn(response.status_code, [200, 201])
                self.assertEqual(response.json()["status"], "CREATED")
                job_list.add(
                    (response.json()["job_id"], pp[1], content)
                )

        while job_list:
            entity = job_list.pop()
            time.sleep(10)
            response = self.__get_result(entity[0])
            print_response_body(response)
            self.assertIn(response.status_code, [200, 201])
            self.assertIn(response.json()["status"], ["OK", "WAITING", "PROCESSING"])
            if response.json()["status"] == "OK":
                tmp_result(response.json()["result"], entity[1])
                log(log_filename, f"{entity[1]},{purify_content(entity[2])},{purify_content(response.json()['result'])}")
                continue
            job_list.add(entity)

    def test_4_reply(self):
        log_filename = time.strftime("%Y-%m-%d %H:%M:%S") + " reply.csv"
        log(log_filename, "file_name,input,output")
        job_list = set()
        for pp in file_list("tmp"):
            with open(pp[0], "r") as file:
                content = file.read()
                response = r.post(
                    self.URL,
                    json={
                        "model": "reply",
                        "content": {
                            "reply_summary": content
                        },
                        "business_id": BUSINESS_ID
                    }
                )
                print_response_body(response)
                self.assertIn(response.status_code, [200, 201])
                self.assertEqual(response.json()["status"], "CREATED")
                job_list.add(
                    (response.json()["job_id"], pp[1], content)
                )

        while job_list:
            entity = job_list.pop()
            time.sleep(10)
            response = self.__get_result(entity[0])
            print_response_body(response)
            self.assertIn(response.status_code, [200, 201])
            self.assertIn(response.json()["status"], ["OK", "WAITING", "PROCESSING"])
            if response.json()["status"] == "OK":
                log(log_filename, f"{entity[1]},{purify_content(entity[2])},{purify_content(response.json()['result'])}")
                continue
            job_list.add(entity)


if __name__ == "__main__":
    unittest.main()
