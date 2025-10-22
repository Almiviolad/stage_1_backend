# 🧠 String Analyzer API

A sleek Flask-based web app that analyzes and stores strings intelligently — checking palindromes, counting words, generating hashes, and more. Built with SQLAlchemy, powered by clean architecture, and ready for extension.

---

## 🚀 Overview

This project is a RESTful Flask application for analyzing and managing strings.  
It can compute multiple properties of a given string such as:

- **Length**
- **Word count**
- **Palindrome check**
- **Character map**
- **SHA256 hash**
- **Unique characters**

The app is modular, database-backed, and designed for easy scaling or integration into larger systems.

---

## 🧩 Features

- **Flask + SQLAlchemy ORM** — Clean, scalable, and Pythonic.
- **Environment-based config** — Uses `.env` for flexible deployment.
- **Structured routes and models** — Readable and maintainable.
- **Error-handling middleware** — No cryptic stack traces for users.
- **Extensible architecture** — Add more analyses or models easily.

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/string-analyzer.git
cd string-analyzer