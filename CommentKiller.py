import tkinter as tk
from tkinter import scrolledtext, OptionMenu, StringVar, messagebox, Frame, Label
import re
import json # json 모듈 임포트

# 임시 표시자 정의 (이전과 동일)
PLACEHOLDER_PREFIX = "__COMMENT_KILLER_STR_LITERAL_"
PLACEHOLDER_SUFFIX = "__"

DEFAULT_LANGUAGES_FILE = "languages.json" # JSON 파일명 정의

def load_language_definitions(filepath=DEFAULT_LANGUAGES_FILE):
    """
    지정된 경로의 JSON 파일에서 언어 정의를 불러옵니다.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            definitions = json.load(f)
        # 로드 성공 시 간단한 메시지 (디버깅용, 실제 배포 시 제거 가능)
        # print(f"'{filepath}'에서 언어 정의를 성공적으로 불러왔습니다.")
        return definitions
    except FileNotFoundError:
        messagebox.showerror("파일 오류", f"언어 정의 파일({filepath})을 찾을 수 없습니다. 기본값 없이 프로그램을 시작합니다.")
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("JSON 오류", f"언어 정의 파일({filepath})의 형식이 잘못되었습니다. 유효한 JSON인지 확인해주세요.")
        return {}
    except Exception as e:
        messagebox.showerror("로드 오류", f"언어 정의 파일({filepath})을 불러오는 중 오류 발생: {e}")
        return {}

def remove_comments_smarter(code, language_name, all_language_definitions): # 세 번째 인자 추가
    """
    주어진 코드에서 선택된 언어의 주석을 제거합니다. (문자열 리터럴 보호)
    all_language_definitions: JSON에서 로드된 전체 언어 정의 딕셔너리.
    """
    if language_name not in all_language_definitions:
        messagebox.showerror("오류", f"'{language_name}' 언어는 아직 지원되지 않습니다 (정의 파일 확인 필요).")
        return code # 원본 코드 반환

    lang_spec = all_language_definitions[language_name]
    string_patterns = lang_spec.get("strings", [])
    comment_patterns = lang_spec.get("comments", [])

    extracted_strings = []
    current_code = code
    placeholder_idx_counter = 0

    if string_patterns:
        for str_pattern_regex in string_patterns:
            processed_parts = []
            last_end_pos = 0
            for match in re.finditer(str_pattern_regex, current_code):
                start_match, end_match = match.span()
                processed_parts.append(current_code[last_end_pos:start_match])
                
                original_string = match.group(0)
                extracted_strings.append(original_string)
                placeholder = f"{PLACEHOLDER_PREFIX}{placeholder_idx_counter}{PLACEHOLDER_SUFFIX}"
                processed_parts.append(placeholder)
                
                placeholder_idx_counter += 1
                last_end_pos = end_match
            
            processed_parts.append(current_code[last_end_pos:])
            current_code = "".join(processed_parts)

    code_with_strings_replaced = current_code

    for _, comment_pattern_regex in comment_patterns: # comment_patterns는 [이름, 패턴] 리스트
        code_with_strings_replaced = re.sub(comment_pattern_regex, "", code_with_strings_replaced)

    final_code = code_with_strings_replaced
    for i in range(len(extracted_strings) - 1, -1, -1):
        placeholder_to_restore = f"{PLACEHOLDER_PREFIX}{i}{PLACEHOLDER_SUFFIX}"
        final_code = final_code.replace(placeholder_to_restore, extracted_strings[i], 1)

    lines = final_code.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    processed_code_final = "\n".join(non_empty_lines)

    return processed_code_final


class CommentKillerApp:
    def __init__(self, master):
        self.master = master
        master.title("CommentKiller - 주석 제거기 (JSON 정의)")
        master.geometry("900x600")

        # 애플리케이션 시작 시 언어 정의 로드
        self.language_definitions = load_language_definitions()

        # --- 상단 프레임: 언어 선택 ---
        top_frame = Frame(master, pady=10)
        top_frame.pack(fill="x", padx=10)

        Label(top_frame, text="프로그래밍 언어 선택:", padx=5).pack(side="left")
        self.language_var = StringVar(master)
        
        lang_keys = list(self.language_definitions.keys())
        if lang_keys:
            self.language_var.set(lang_keys[0]) # 첫 번째 언어를 기본값으로
            self.language_menu = OptionMenu(top_frame, self.language_var, *lang_keys)
        else:
            # 로드된 언어가 없을 경우의 처리
            self.language_var.set("정의된 언어 없음")
            self.language_menu = OptionMenu(top_frame, self.language_var, "정의된 언어 없음")
        
        self.language_menu.pack(side="left", padx=5)

        # --- 중앙 프레임: 텍스트 영역 (이전과 동일) ---
        text_frame = Frame(master)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)

        input_frame = Frame(text_frame)
        input_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        Label(input_frame, text="주석이 있는 원본 코드:", pady=5).pack(anchor="w")
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=15, undo=True)
        self.input_text.pack(fill="both", expand=True)

        output_frame = Frame(text_frame)
        output_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        Label(output_frame, text="주석 제거된 코드:", pady=5).pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=15, undo=True)
        self.output_text.pack(fill="both", expand=True)
        self.output_text.config(state=tk.DISABLED)

        # --- 하단 프레임: 버튼 (이전과 동일) ---
        bottom_frame = Frame(master, pady=10)
        bottom_frame.pack(fill="x")

        self.remove_button = tk.Button(bottom_frame, text="주석 제거 실행!", command=self.process_remove_comments, width=20, height=2)
        self.remove_button.pack()

    def process_remove_comments(self):
        source_code = self.input_text.get("1.0", tk.END).strip()
        selected_language = self.language_var.get()

        if not source_code:
            messagebox.showwarning("입력 필요", "제거할 코드를 좌측에 입력해주세요.")
            return

        if selected_language == "정의된 언어 없음" or not self.language_definitions:
             messagebox.showwarning("언어 문제", "선택할 언어가 없거나 언어 정의 파일을 불러오지 못했습니다.")
             return

        # 로드된 전체 언어 정의를 remove_comments_smarter 함수에 전달
        cleaned_code = remove_comments_smarter(source_code, selected_language, self.language_definitions)

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.INSERT, cleaned_code)
        self.output_text.config(state=tk.DISABLED)
        
        if source_code and not cleaned_code.strip() and source_code.strip():
            messagebox.showinfo("결과", "모든 내용(주석 포함)이 제거되었거나 입력이 주석으로만 이루어져 있었습니다.")
        elif source_code and cleaned_code.strip():
             messagebox.showinfo("성공", f"'{selected_language}' 언어의 주석이 성공적으로 제거되었습니다!")

# --- 4. 메인 프로그램 실행 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CommentKillerApp(root)
    root.mainloop()
