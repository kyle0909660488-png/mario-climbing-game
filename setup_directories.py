######################載入套件######################
import os


######################建立目錄結構######################
def create_directories():
    """
    建立專案所需的目錄結構
    """
    directories = [
        "src",
        "src/characters",
        "src/levels",
        "src/traps",
        "src/enemies",
        "src/ui",
        "src/equipment",
    ]

    base_path = os.path.dirname(os.path.abspath(__file__))

    for directory in directories:
        dir_path = os.path.join(base_path, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f"目錄已建立: {dir_path}")

        # 建立 __init__.py 檔案讓 Python 認得這是套件
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# 此檔案讓 Python 認得這是一個套件\n")
            print(f"初始化檔案已建立: {init_file}")


if __name__ == "__main__":
    create_directories()
    print("專案目錄結構建立完成！")
