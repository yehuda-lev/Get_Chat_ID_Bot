# Contributing

Thank you for considering contributing to this project! We appreciate your effort in helping improve it. Below are the guides for contributing new languages and features.

---

## 🚀 Quick Links
- [Contributing a New Language](#-contributing-a-new-language)
- [Contributing New Features](#-contributing-new-features)
- [Getting Help](#-getting-help)

---

## 🌍 Contributing a New Language

If you would like to add support for a new language, follow these steps:

### Prerequisites

- **Python**: Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
- **Git**: Install Git to clone the repository and manage contributions. [Git installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

### Steps to Contribute a New Language

1. **Fork the Repository**
    - Go to the [project's GitHub page](https://github.com/yehuda-lev/Get_Chat_ID_Bot).
    - Click on the "Fork" button to create your copy of the repository.

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/yehuda-lev/Get_Chat_ID_Bot.git
   cd Get_Chat_ID_Bot
   ```

3. **Install Dependencies**
   Create a virtual environment and install the required libraries:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   pip install -r requirements.txt
   ```

4. **Prepare the Language Data**
    - Open `languages.json` and check if the language you want to add already exists.
    - If not, add an entry for your language. Provide:
        - `Code` (ISO 639 format)
        - `NativeName`
        - `Flag`
        - `EnglishName`

5. **Generate the Translation File**
   Use the provided script to generate translations:
   ```bash
   python generate.py <lang_code>
   ```
   Replace `<lang_code>` with the language code of your choice.

6. **Verify the Output**
    - Check the generated `<lang_code>.json` file in the project directory.
    - Ensure translations are correct and formatted properly.

7. **Submit Your Changes**
    - Commit your changes:
      ```bash
      git add .
      git commit -m "Add support for <language>"
      ```
    - Push your changes to your fork:
      ```bash
      git push origin main
      ```
    - Open a pull request on the original repository, describing the new language you added.

> **Note:** Please ensure translations are accurate. You can consult native speakers or reliable sources for verification.

---

## ✨ Contributing New Features

If you have an idea for a new feature or improvement, follow these steps:

### Prerequisites

- Familiarity with Python and Git.
- A clear understanding of the feature you want to add.

### Steps to Contribute a Feature

1. **Fork and Clone the Repository**
   Follow the same steps as described in the "Contributing a New Language" section to fork and clone the repository.

2. **Create a New Branch**
   ```bash
   git checkout -b feature/<your-feature-name>
   ```

3. **Implement Your Feature**
    - Add your code changes.
    - Ensure they do not break existing functionality.

4. **Test Your Changes**
    - Run the project locally to verify your feature works as intended.

5. **Document Your Changes**
    - Update any relevant documentation to include your new feature.

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: <your-feature-name>"
   ```

7. **Submit Your Changes**
    - Push your changes to your fork:
      ```bash
      git push origin feature/<your-feature-name>
      ```
    - Open a pull request on the original repository, describing your feature.

---

## 💬 Getting Help

If you have any questions, feel free to join our [Telegram support group](https://t.me/GetChatID_Chat). We're here to help! 💬

---

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project. Please see the `LICENSE` file in the repository for details.

