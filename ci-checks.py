import os
import subprocess


print("\n*** flake8 ***\n")
flake = subprocess.call(["python", "-m", "flake8", "--max-line-length=120"])

print("\n\n*** pyright ***\n")
right = subprocess.call(["python", "-m", "pyright", "--project", "pyrightconfig.json"])

print("\n\n*** pydocstyle ***\n")
docstyle = subprocess.call(
    [
        "python",
        "-m",
        "pydocstyle",
        "--add-ignore=D100",
        "--add-select=D212",
        "./datasim",
    ]
)

print("\n\n*** pytest ***\n")
test = subprocess.call(["python", "-m", "pytest", "--cov=datasim/"])

print("\n\n*** sphinx ***\n")
os.chdir("docs")
docs = subprocess.call(["python", "-m", "sphinx", "-M", "html", "source", "build"])

print("\n\nSummary\n=======\n")

if flake == 0:
    print("✔️   flake8      Success")
else:
    print("❌  flake8      Failed")
if right == 0:
    print("✔️   pyright     Success")
else:
    print("❌  pyright     Failed")
if docstyle == 0:
    print("✔️   pydocstyle  Success")
else:
    print("❌  pydocstyle  Failed")
if test == 0:
    print("✔️   pytest      Success")
else:
    print("❌  pytest      Failed")
if docs == 0:
    print("✔️   sphinx      Success")
else:
    print("❌  sphinx      Failed")

total = (
    (1 if flake == 0 else 0)
    + (1 if right == 0 else 0)
    + (1 if docstyle == 0 else 0)
    + (1 if test == 0 else 0)
    + (1 if docs == 0 else 0)
)

print(f"\n{total}/5 passed.")
print("Ready to push!" if total == 5 else "Work to do...")
