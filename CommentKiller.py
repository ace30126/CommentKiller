import tkinter as tk
from tkinter import scrolledtext, OptionMenu, StringVar, messagebox, Frame, Label
import re
import json
import os # 파일 및 디렉토리 관리를 위해 추가
from datetime import datetime # 타임스탬프 생성을 위해 추가

# --- 상수 정의 ---
PLACEHOLDER_PREFIX = "__COMMENT_KILLER_STR_LITERAL_"
PLACEHOLDER_SUFFIX = "__"
DEFAULT_LANGUAGES_FILE = "languages.json"
BACKUP_DIR = "comment_killer_backups" # 백업 파일 저장 디렉토리
LOG_FILE = os.path.join(BACKUP_DIR, "comment_killer_processing_log.txt") # 로그 파일 경로

# --- 언어 정의 로드 함수 (이전과 동일) ---
def load_language_definitions(filepath=DEFAULT_LANGUAGES_FILE):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            definitions = json.load(f)
        return definitions
    except FileNotFoundError:
        messagebox.showerror("파일 오류", f"언어 정의 파일({filepath})을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("JSON 오류", f"언어 정의 파일({filepath})의 형식이 잘못되었습니다.")
        return {}
    except Exception as e:
        messagebox.showerror("로드 오류", f"언어 정의 파일({filepath}) 로드 중 오류: {e}")
        return {}

# --- 스마트 주석 제거 함수 (이전과 동일) ---
def remove_comments_smarter(code, language_name, all_language_definitions):
    if language_name not in all_language_definitions:
        messagebox.showerror("오류", f"'{language_name}' 언어는 아직 지원되지 않습니다 (정의 파일 확인 필요).")
        return code

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

    for _, comment_pattern_regex in comment_patterns:
        code_with_strings_replaced = re.sub(comment_pattern_regex, "", code_with_strings_replaced)

    final_code = code_with_strings_replaced
    for i in range(len(extracted_strings) - 1, -1, -1):
        placeholder_to_restore = f"{PLACEHOLDER_PREFIX}{i}{PLACEHOLDER_SUFFIX}"
        final_code = final_code.replace(placeholder_to_restore, extracted_strings[i], 1)

    lines = final_code.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    processed_code_final = "\n".join(non_empty_lines)
    return processed_code_final

# --- 백업 디렉토리 및 로그 파일 준비 함수 ---
def ensure_backup_infrastructure():
    """백업 디렉토리와 초기 로그 파일을 준비합니다."""
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR)
        except OSError as e:
            messagebox.showerror("백업 오류", f"백업 디렉토리 생성 실패: {BACKUP_DIR}\n{e}")
            return False # 디렉토리 생성 실패

    # 로그 파일이 없으면 헤더와 함께 생성
    if not os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "w", encoding="utf-8") as logf:
                logf.write("CommentKiller 처리 및 백업 로그\n")
                logf.write("=" * 40 + "\n")
        except Exception as e:
            # 로그 파일 생성 실패는 치명적이지 않으므로 경고만 표시
            messagebox.showwarning("로그 오류", f"로그 파일 생성 실패: {LOG_FILE}\n{e}")
    return True # 인프라 준비 완료 (또는 디렉토리는 이미 존재)

# --- CommentKiller 애플리케이션 UI 클래스 (수정됨) ---
class CommentKillerApp:
    def __init__(self, master):
        self.master = master
        master.title("CommentKiller - 주석 제거기 (백업 기능)")
        master.geometry("900x650") # 높이 약간 늘림 (필요시)

        self.language_definitions = load_language_definitions()
        self.backup_infra_ok = ensure_backup_infrastructure() # 백업 인프라 준비

        # --- UI 요소들 (이전과 동일하게 설정) ---
        top_frame = Frame(master, pady=10)
        top_frame.pack(fill="x", padx=10)
        Label(top_frame, text="프로그래밍 언어 선택:", padx=5).pack(side="left")
        self.language_var = StringVar(master)
        lang_keys = list(self.language_definitions.keys())
        if lang_keys:
            self.language_var.set(lang_keys[0])
            self.language_menu = OptionMenu(top_frame, self.language_var, *lang_keys)
        else:
            self.language_var.set("정의된 언어 없음")
            self.language_menu = OptionMenu(top_frame, self.language_var, "정의된 언어 없음")
        self.language_menu.pack(side="left", padx=5)

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

        bottom_frame = Frame(master, pady=10)
        bottom_frame.pack(fill="x")
        self.remove_button = tk.Button(bottom_frame, text="주석 제거 실행!", command=self.process_remove_comments, width=20, height=2)
        self.remove_button.pack()

    def process_remove_comments(self):
        if not self.backup_infra_ok:
            messagebox.showerror("오류", "백업 시스템이 준비되지 않아 처리를 중단합니다.\n프로그램을 재시작하거나 폴더 권한을 확인해주세요.")
            return

        original_code_full = self.input_text.get("1.0", tk.END) # 백업을 위해 전체 텍스트 가져오기 (마지막 개행 포함)
        source_code_to_process = original_code_full.strip() # 처리를 위해 앞뒤 공백 제거
        selected_language = self.language_var.get()

        if not source_code_to_process: # 처리할 코드가 실제로 있는지 확인
            messagebox.showwarning("입력 필요", "제거할 코드를 좌측에 입력해주세요.")
            return

        if selected_language == "정의된 언어 없음" or not self.language_definitions:
             messagebox.showwarning("언어 문제", "선택할 언어가 없거나 언어 정의 파일을 불러오지 못했습니다.")
             return

        # --- 백업 로직 시작 ---
        backup_info_for_user = ""
        backup_filename_leaf = "" # 초기화
        try:
            # 파일 이름에 사용할 안전한 언어 이름 생성 (특수문자 제거)
            safe_lang_name = "".join(c if c.isalnum() else "_" for c in selected_language)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3] # 밀리초까지
            backup_filename_leaf = f"backup_{timestamp}_{safe_lang_name}.txt.back"
            backup_filepath = os.path.join(BACKUP_DIR, backup_filename_leaf)

            with open(backup_filepath, "w", encoding="utf-8") as bf:
                bf.write(original_code_full) # 원본 전체 내용 저장

            # 로그 파일에 기록
            try:
                with open(LOG_FILE, "a", encoding="utf-8") as logf:
                    log_entry = (f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                                 f"백업 파일: {backup_filename_leaf}, 언어: {selected_language}\n")
                    logf.write(log_entry)
            except Exception as log_e:
                # 로그 기록 실패는 경고만 표시, 주 기능에 영향 주지 않음
                 messagebox.showwarning("로그 기록 오류", f"백업 로그 기록 중 오류 발생: {log_e}")


            backup_info_for_user = (f"\n\n[백업 성공]\n"
                                    f"원본이 '{backup_filename_leaf}'로 저장되었습니다.\n"
                                    f"(저장 위치: {os.path.abspath(BACKUP_DIR)})")
        except Exception as e:
            backup_error_details = f"원본 코드 백업 중 오류 발생:\n{e}"
            messagebox.showwarning("백업 오류", backup_error_details) # 백업 실패 시 즉시 알림
            backup_info_for_user = f"\n\n[백업 실패]\n{backup_error_details}"
        # --- 백업 로직 끝 ---

        # 주석 제거 로직 실행
        cleaned_code = remove_comments_smarter(source_code_to_process, selected_language, self.language_definitions)

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.INSERT, cleaned_code)
        self.output_text.config(state=tk.DISABLED)

        # 최종 결과 메시지
        result_summary = ""
        if source_code_to_process and not cleaned_code.strip() and source_code_to_process.strip():
            result_summary = "모든 내용(주석 포함)이 제거되었거나 입력이 주석으로만 이루어져 있었습니다."
        elif source_code_to_process and cleaned_code.strip():
            result_summary = f"'{selected_language}' 언어의 주석이 성공적으로 제거되었습니다!"
        else: # 입력이 처음부터 비어있었던 경우 (위에서 이미 처리했지만 방어적으로)
            result_summary = "처리할 코드가 없었습니다."

        messagebox.showinfo("처리 결과", result_summary + backup_info_for_user)

# --- 메인 프로그램 실행 부분 (이전과 동일) ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CommentKillerApp(root)
    root.mainloop()
