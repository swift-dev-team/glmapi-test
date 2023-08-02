import unittest
import requests as r
import os
import os.path as path
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

unittest.TestLoader.sortTestMethodsUsing = None

HOST=os.getenv("HOST")
BUSINESS_ID="41315905-e402-4eae-bb2f-df20e2d11a86"
PWD=Path(path.abspath("./"))

def print_response_body(response):
    print("\033[93m" + response.text + "\033[0m")

def log(filename, val):
    OUTPUT_DIR=PWD/"data"/"output"/"1"
    if not path.exists(OUTPUT_DIR):
        Path.mkdir(OUTPUT_DIR, parents=True, exist_ok=True)
    with open(OUTPUT_DIR/filename, "a") as file:
        file.write(val + "\n")


class TestFileAction(unittest.TestCase):
    INPUT_DIR=PWD / "data" / "input" / "1"
    FILE1=INPUT_DIR / "1.basic_info.txt"
    FILE2=INPUT_DIR / "2.产品信息202305242.xlsx"

    def __get_vector_ids(self):
        url = f"{HOST}/v1/vs/{BUSINESS_ID}"
        response = r.get(url)
        return response

    def test_upload(self):
        url = f"{HOST}/v1/vs"
        with open(self.FILE1, "rb") as file:
            response = r.post(
                url,
                files={
                    "file": (path.basename(self.FILE1), file, "text/plain")
                },
                data={
                    "business_id": BUSINESS_ID,
                    "metadata": '{"name": "1.basic_info.txt"}'
                }
            )
            print_response_body(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "OK")
        log("file_test_action.txt", f"test_upload\tOK\t{response.text}")

    def test_get_vector_id(self):
        response = self.__get_vector_ids()
        print_response_body(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "OK")
        log("file_test_action.txt", f"test_get_vector_id\tOK\t{response.text}")

    def test_change_file(self):
        url = f"{HOST}/v1/vs"
        with open(self.FILE2, "rb") as file:
            response = r.put(
                url,
                files={
                    "file": (path.basename(self.FILE2), file, "text/plain")
                },
                data={
                    "business_id": BUSINESS_ID,
                    "metadata": '{"name": "2.产品信息202305242.xlsx"}'
                }
            )
            print_response_body(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "OK")
        log("file_test_action.txt", f"test_change_file\tOK\t{response.text}")

    def test_delete_single_file(self):
        url = f"{HOST}/v1/vs"
        response = r.delete(
            url,
            json={
                "business_id": BUSINESS_ID,
                "metadata": '{"name": "1.basic_info.txt"}',
                "ids": []
            }
        )
        print_response_body(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "OK")
        log("file_test_action.txt", f"test_delete_single_file\tOK\t{response.text}")

    def test_delete_all_files(self):
        res = self.__get_vector_ids()
        url = f"{HOST}/v1/vs"
        response = r.delete(
            url,
            json={
                "business_id": BUSINESS_ID,
                "metadata": "",
                "ids": res.json()["result"]
            }
        )
        print_response_body(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "OK")
        log("file_test_action.txt", f"test_delete_all_files\tOK\t{response.text}")

if __name__ == "__main__":
    unittest.main()
