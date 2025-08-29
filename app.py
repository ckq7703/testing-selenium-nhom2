from flask import Flask, render_template, jsonify, request
import json
import os


app = Flask(__name__)

def normalize_value(value):
    """Chuyển field dict {text, repeat} sang dạng hiển thị dễ đọc"""
    if isinstance(value, dict) and "text" in value and "repeat" in value:
        return f"{value['text']} (repeat {value['repeat']})"
    return value


@app.route("/challenges")
def challenges():
    with open("tests/data/challenge_test_data.json", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for section, cases in data.items():
        for case in cases:
            input_data = {
                "title": (case.get("title", "")),
                "description": (case.get("description", "")),
                "guide": normalize_value(case.get("guide", "")),
                "points": normalize_value(case.get("points", "")),
                "challengen_id": normalize_value(case.get("challenge_id", "")),
                "public": case.get("public")
            }

            rows.append({
                "type": section,   # ví dụ: add_challenge, edit_challenge...
                "desc": case.get("desc"),
                "input": json.dumps(input_data, ensure_ascii=False, indent=2),
                "output": case.get("expected"),
                "result": ""       # để trống, có thể cập nhật sau
            })

    return render_template("challenges.html", rows=rows)

import json

def normalize_value(value):
    """Xử lý giá trị có thể là dict repeat hoặc string."""
    if isinstance(value, dict) and "text" in value and "repeat" in value:
        return value["text"] * value["repeat"]
    return value

@app.route("/flags")
def flags():
    with open("tests/data/flag_test_data.json", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for section, cases in data.items():
        for case in cases:
            # gom input thành 1 object
            input_data = {
                "challenge_title": case.get("challenge_title"),
                "flag_value": case.get("flag_value"),
                "description": (case.get("description", "")),
                "is_image": case.get("is_image"),
                "image_path": case.get("image_path"),
                "flag_id": case.get("flag_id"),
                "scenario": case.get("scenario")
            }
            rows.append({
                "type": section,        # add_flag, edit_flag, delete_flag
                "desc": case.get("desc"),
                "input": json.dumps(input_data, ensure_ascii=False, indent=2),
                "output": case.get("expected"),
                "result": ""            # để trống, có thể fill sau
            })

    return render_template("flags.html", rows=rows)

@app.route("/login")
def login_tests():
    with open("tests/data/login_test_data.json", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for case in data.get("login", []):
        rows.append({
            "type": "login",   # loại test
            "desc": case.get("desc"),
            "input": json.dumps({
                "username": case.get("username"),
                "password": case.get("password")
            }, ensure_ascii=False, indent=2),
            "output": case.get("expected"),
            "result": ""   # để trống cho người dùng nhập sau
        })

    return render_template("login.html", rows=rows)


@app.route("/login/update", methods=["POST"])
def login_update():
    req = request.get_json()
    index = req.get("index")
    new_input = req.get("input")

    with open("tests/data/login_test_data.json", encoding="utf-8") as f:
        data = json.load(f)

    try:
        parsed = json.loads(new_input)  # kiểm tra input là JSON hợp lệ
    except json.JSONDecodeError:
        return jsonify({"message": "Input không phải JSON hợp lệ"}), 400

    # cập nhật lại dữ liệu
    if 0 <= int(index) < len(data["login"]):
        data["login"][int(index)]["username"] = parsed.get("username", "")
        data["login"][int(index)]["password"] = parsed.get("password", "")

        # ghi lại file
        with open("tests/data/login_test_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return jsonify({"message": "Cập nhật thành công"})
    else:
        return jsonify({"message": "Index không hợp lệ"}), 400



@app.route("/users")
def users():
    with open("tests/data/user_test_data.json", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    # add_user
    for case in data.get("add_user", []):
        rows.append({
            "type": "add_user",
            "desc": case.get("desc"),
            "input": json.dumps({
                "username": case.get("username"),
                "password": case.get("password"),
                "role": case.get("role")
            }, ensure_ascii=False, indent=2),
            "output": case.get("expected")
        })

    # edit_user
    for case in data.get("edit_user", []):
        rows.append({
            "type": "edit_user",
            "desc": case.get("desc"),
            "input": json.dumps({
                "username": case.get("username"),
                "password": case.get("password"),
                "role": case.get("role")
            }, ensure_ascii=False, indent=2),
            "output": case.get("expected")
        })

    # delete_user
    for case in data.get("delete_user", []):
        rows.append({
            "type": "delete_user",
            "desc": case.get("desc"),
            "input": json.dumps({
                "scenario": case.get("scenario"),
                "user_id": case.get("user_id"),
                "username": case.get("username"),
                "page_number": case.get("page_number")
            }, ensure_ascii=False, indent=2),
            "output": case.get("expected")
        })

    return render_template("users.html", rows=rows)


@app.route("/users/update", methods=["POST"])
def users_update():
    try:
        data = request.get_json()
        index = int(data.get("index"))
        new_input = data.get("input")

        file_path = os.path.join("tests", "data", "user_test_data.json")
        with open(file_path, encoding="utf-8") as f:
            raw_data = json.load(f)

        # Gom toàn bộ test cases thành list giống lúc render_template
        all_cases = []
        section_map = []  # lưu mapping: (section, idx_in_section)

        for section in ["add_user", "edit_user", "delete_user"]:
            for i, case in enumerate(raw_data.get(section, [])):
                all_cases.append(case)
                section_map.append((section, i))

        if index < 0 or index >= len(all_cases):
            return jsonify({"message": "Index không hợp lệ"}), 400

        section, case_index = section_map[index]

        # Parse lại input JSON được gửi từ textarea
        try:
            parsed_input = json.loads(new_input)
        except Exception as e:
            return jsonify({"message": "Input không phải JSON hợp lệ", "error": str(e)}), 400

        # Cập nhật fields của case
        for key, val in parsed_input.items():
            raw_data[section][case_index][key] = val

        # Ghi lại file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)

        return jsonify({
            "message": f"User test case {index} trong {section} đã được cập nhật",
            "new_input": parsed_input
        })

    except Exception as e:
        return jsonify({"message": "Lỗi xử lý", "error": str(e)}), 500
    
    

if __name__ == "__main__":
    app.run(debug=True)
