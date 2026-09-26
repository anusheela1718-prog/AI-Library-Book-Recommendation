"""
generate_dataset.py - Creates the sample data for the project.

Run:  python scripts/generate_dataset.py

It writes:
  dataset/books.csv               (108 demo books)
  dataset/students.json           (10 demo students)
  dataset/reading_history.json    (demo reading history)
  frontend/images/B001.svg ...    (simple book-cover images)

All titles/authors/descriptions are ORIGINAL demo metadata (no copyrighted text).
"""
import csv
import json
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (subject, category, keywords, [3 concept phrases])
TOPICS = [
    ("Java", "Programming", "java, oop, classes, inheritance, collections, exception handling, jvm",
     ["object-oriented programming", "classes, objects and inheritance", "collections and exception handling"]),
    ("Python", "Programming", "python, scripting, functions, modules, file handling, libraries",
     ["variables, loops and functions", "modules and file handling", "useful Python libraries"]),
    ("C", "Programming", "c language, pointers, arrays, structures, memory, functions",
     ["pointers and arrays", "structures and functions", "dynamic memory allocation"]),
    ("C++", "Programming", "c++, oop, templates, stl, pointers, classes",
     ["classes and objects in C++", "templates and the STL", "operator overloading and pointers"]),
    ("JavaScript", "Web Development", "javascript, dom, es6, events, async, functions, browser",
     ["the DOM and browser events", "ES6 features and functions", "asynchronous programming and APIs"]),
    ("Web Development", "Web Development", "web development, frontend, backend, responsive design, http, apis",
     ["frontend and backend basics", "responsive websites", "HTTP requests and REST APIs"]),
    ("HTML", "Web Development", "html5, tags, forms, semantic elements, links, tables",
     ["HTML5 tags and structure", "forms and tables", "semantic elements and accessibility"]),
    ("CSS", "Web Development", "css3, flexbox, grid, selectors, responsive design, animations",
     ["selectors and the box model", "flexbox and grid layouts", "responsive design and animations"]),
    ("SQL", "Databases", "sql, queries, joins, select, insert, aggregation, subqueries",
     ["SELECT queries and filtering", "joins and aggregation", "subqueries and views"]),
    ("DBMS", "Databases", "dbms, er model, normalization, transactions, relational model, indexing",
     ["the ER model and relational model", "normalization", "transactions and indexing"]),
    ("Computer Networks", "Networking", "networks, tcp ip, osi model, routing, protocols, ip addressing",
     ["the OSI and TCP/IP models", "IP addressing and routing", "network protocols"]),
    ("Operating Systems", "Systems", "operating system, process, scheduling, memory management, deadlock, file system",
     ["processes and CPU scheduling", "memory management", "deadlocks and file systems"]),
    ("Data Structures", "Data Structures and Algorithms", "data structures, arrays, linked list, stack, queue, trees, graphs",
     ["arrays and linked lists", "stacks and queues", "trees and graphs"]),
    ("Algorithms", "Data Structures and Algorithms", "algorithms, sorting, searching, recursion, dynamic programming, complexity",
     ["sorting and searching", "recursion and dynamic programming", "time and space complexity"]),
    ("Artificial Intelligence", "Artificial Intelligence", "ai, artificial intelligence, search, knowledge representation, agents, expert systems",
     ["intelligent agents", "search strategies and knowledge representation", "expert systems"]),
    ("Machine Learning", "Artificial Intelligence", "machine learning, supervised learning, regression, classification, clustering, model evaluation",
     ["regression and classification", "clustering", "model evaluation and overfitting"]),
    ("Deep Learning", "Artificial Intelligence", "deep learning, neural networks, cnn, rnn, backpropagation, tensorflow",
     ["neural networks and backpropagation", "convolutional networks for images", "recurrent networks for sequences"]),
    ("Data Science", "Data Science", "data science, data analysis, pandas, visualization, statistics, data cleaning",
     ["data cleaning with pandas", "statistics for analysis", "data visualization"]),
    ("Cyber Security", "Cyber Security", "cyber security, encryption, malware, firewall, authentication, ethical hacking",
     ["encryption and authentication", "malware and firewalls", "ethical hacking basics"]),
    ("Cloud Computing", "Cloud Computing", "cloud computing, virtualization, iaas, paas, saas, scalability, serverless",
     ["IaaS, PaaS and SaaS", "virtualization", "scalability and serverless computing"]),
    ("AWS", "Cloud Computing", "aws, ec2, s3, lambda, dynamodb, iam, cloud services",
     ["EC2 and S3 storage", "Lambda and serverless functions", "DynamoDB and IAM security"]),
    ("Software Engineering", "Software Engineering", "software engineering, sdlc, requirements, uml, agile, design, maintenance",
     ["the software development life cycle", "requirements and UML design", "agile methods"]),
    ("Software Testing", "Software Engineering", "software testing, test cases, unit testing, black box, white box, automation, bug tracking",
     ["test case design", "black box and white box testing", "unit testing and automation"]),
    ("DevOps", "Software Engineering", "devops, ci cd, docker, git, automation, monitoring, containers",
     ["Git version control", "CI/CD pipelines", "Docker containers and monitoring"]),
    ("IoT", "Emerging Technologies", "iot, sensors, arduino, raspberry pi, mqtt, embedded, smart devices",
     ["sensors and actuators", "Arduino and Raspberry Pi projects", "MQTT and smart devices"]),
    ("Blockchain", "Emerging Technologies", "blockchain, distributed ledger, smart contracts, cryptocurrency, consensus, hashing",
     ["hashing and distributed ledgers", "consensus methods", "smart contracts"]),
    ("Computer Architecture", "Computer Architecture", "computer architecture, cpu, memory hierarchy, pipelining, instruction set, cache, assembly",
     ["CPU organization", "pipelining and instruction sets", "cache and memory hierarchy"]),
]

LEVELS = [
    ("Fundamentals", "beginner", "a beginner-friendly introduction for first and second year students"),
    ("Practical Guide", "projects", "a hands-on guide with lab exercises and mini projects"),
    ("Advanced Concepts", "advanced", "an in-depth book for senior students who want to go deeper"),
    ("Exam and Interview Guide", "interview", "a revision guide with solved questions for exams, viva and placement interviews"),
]

AUTHORS = [
    "Ananya Rao", "Rohan Mehta", "Priya Nair", "Karthik Subramanian", "Meera Iyer", "Vikram Singh",
    "Sneha Kulkarni", "Arjun Reddy", "Divya Menon", "Sanjay Patel", "Lakshmi Narayan", "Imran Sheikh",
    "Pooja Verma", "Harish Kumar", "Neha Gupta", "Suresh Babu", "Kavya Pillai", "Ravi Chandran",
    "Aditi Joshi", "Manoj Das", "Farah Khan", "Deepak Rao", "Swathi Krishnan", "Nikhil Bhat",
]

COLORS = {
    "Programming": "#2A5DB0", "Web Development": "#0E8A7D", "Databases": "#7A4FB5",
    "Networking": "#C25B1F", "Systems": "#4B5563", "Data Structures and Algorithms": "#B4295A",
    "Artificial Intelligence": "#1B3A6B", "Data Science": "#2F855A", "Cyber Security": "#8B1E2D",
    "Cloud Computing": "#1F7AA8", "Software Engineering": "#8A6D0B", "Emerging Technologies": "#5B3FA0",
    "Computer Architecture": "#374151",
}


def build_books():
    books = []
    n = 0
    for t_index, (subject, category, keywords, concepts) in enumerate(TOPICS):
        c1, c2, c3 = concepts
        for l_index, (suffix, level_kw, level_desc) in enumerate(LEVELS):
            n += 1
            title = f"{subject} {suffix}"
            if l_index == 0:
                body = f"It explains {c1}, {c2} and {c3} with simple examples."
            elif l_index == 1:
                body = f"Readers practise {c2} and {c3} through step-by-step exercises and small projects."
            elif l_index == 2:
                body = f"It gives a deeper look at {c3} and {c1}, with design tips and case studies."
            else:
                body = f"It revises {c1}, {c2} and {c3} with short notes, solved problems and viva questions."
            description = f"{title} is {level_desc} on {subject}. {body}"
            books.append({
                "book_id": f"B{n:03d}",
                "title": title,
                "author": AUTHORS[(t_index + l_index * 5) % len(AUTHORS)],
                "category": category,
                "subject": subject,
                "keywords": f"{keywords}, {level_kw}",
                "description": description,
                "image_url": f"images/B{n:03d}.svg",
            })
    return books


def wrap(text, width=16):
    words, lines, line = text.split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > width and line:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        lines.append(line)
    return lines[:4]


def write_cover(book):
    color = COLORS.get(book["category"], "#2A5DB0")
    lines = wrap(book["title"])
    text = "".join(
        f'<text x="20" y="{110 + i * 26}" font-family="Georgia,serif" font-size="20" fill="#fff" font-weight="bold">{escape(l)}</text>'
        for i, l in enumerate(lines)
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="280" viewBox="0 0 200 280">'
        f'<rect width="200" height="280" rx="6" fill="{color}"/>'
        '<rect x="0" y="0" width="14" height="280" fill="rgba(0,0,0,0.25)"/>'
        '<rect x="20" y="30" width="60" height="4" fill="#F2A900"/>'
        f'<text x="20" y="60" font-family="Arial,sans-serif" font-size="11" fill="#dbe6f7">{escape(book["category"][:26])}</text>'
        f'{text}'
        f'<text x="20" y="262" font-family="Arial,sans-serif" font-size="12" fill="#ffffff">{escape(book["author"])}</text>'
        '</svg>'
    )
    with open(os.path.join(ROOT, "frontend", "images", book["book_id"] + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)


def main():
    books = build_books()
    os.makedirs(os.path.join(ROOT, "dataset"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "frontend", "images"), exist_ok=True)

    with open(os.path.join(ROOT, "dataset", "books.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["book_id", "title", "author", "category", "subject", "keywords", "description", "image_url"])
        w.writeheader()
        w.writerows(books)
    for b in books:
        write_cover(b)

    def bid(subject, level=0):
        return next(b["book_id"] for b in books if b["subject"] == subject and b["title"].endswith(LEVELS[level][0]))

    students = [
        {"studentId": "ST001", "name": "Aarav Kumar", "department": "BCA", "year": "3", "interests": ["Java", "Programming"], "subjects": ["Programming"]},
        {"studentId": "ST002", "name": "Diya Sharma", "department": "BCA", "year": "3", "interests": ["Machine Learning", "AI"], "subjects": ["Artificial Intelligence"]},
        {"studentId": "ST003", "name": "Rahul Nair", "department": "BCA", "year": "2", "interests": ["Web Development", "JavaScript"], "subjects": ["Web Development"]},
        {"studentId": "ST004", "name": "Sana Fathima", "department": "BCA", "year": "3", "interests": ["Cyber Security"], "subjects": ["Cyber Security", "Networking"]},
        {"studentId": "ST005", "name": "Vishal Reddy", "department": "BCA", "year": "1", "interests": ["Python", "Data Science"], "subjects": ["Data Science"]},
        {"studentId": "ST006", "name": "Lavanya Iyer", "department": "BCA", "year": "2", "interests": ["Database", "SQL"], "subjects": ["Databases"]},
        {"studentId": "ST007", "name": "Mohan Raj", "department": "BCA", "year": "3", "interests": ["Cloud Computing", "AWS"], "subjects": ["Cloud Computing"]},
        {"studentId": "ST008", "name": "Keerthi Suresh", "department": "BCA", "year": "1", "interests": ["C", "Programming"], "subjects": ["Programming"]},
        {"studentId": "ST009", "name": "Farhan Ali", "department": "BCA", "year": "2", "interests": ["Software Engineering"], "subjects": ["Software Engineering"]},
        {"studentId": "ST010", "name": "Nisha Thomas", "department": "BCA", "year": "3", "interests": ["Data Science", "Machine Learning"], "subjects": ["Data Science", "Artificial Intelligence"]},
    ]
    history_plan = [
        ("ST001", "Java", 0, 5, "2026-08-01T10:00:00Z"), ("ST001", "Data Structures", 0, 4, "2026-08-05T11:30:00Z"),
        ("ST002", "Machine Learning", 0, 5, "2026-08-02T09:15:00Z"), ("ST002", "Python", 0, 4, "2026-08-06T16:00:00Z"),
        ("ST003", "HTML", 0, 4, "2026-08-03T14:20:00Z"), ("ST003", "CSS", 0, 5, "2026-08-07T10:10:00Z"),
        ("ST004", "Cyber Security", 0, 5, "2026-08-04T12:00:00Z"), ("ST004", "Computer Networks", 0, 3, "2026-08-08T15:45:00Z"),
        ("ST005", "Python", 1, 5, "2026-08-02T17:30:00Z"), ("ST005", "Data Science", 0, 4, "2026-08-09T09:00:00Z"),
        ("ST006", "SQL", 0, 5, "2026-08-03T13:00:00Z"), ("ST006", "DBMS", 0, 4, "2026-08-10T11:00:00Z"),
        ("ST007", "Cloud Computing", 0, 5, "2026-08-04T10:30:00Z"), ("ST007", "AWS", 0, 5, "2026-08-11T14:00:00Z"),
    ]
    history = [
        {"historyId": f"H{i+1:03d}", "studentId": s, "bookId": bid(sub, lv), "selectedAt": ts, "rating": r}
        for i, (s, sub, lv, r, ts) in enumerate(history_plan)
    ]
    with open(os.path.join(ROOT, "dataset", "students.json"), "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2)
    with open(os.path.join(ROOT, "dataset", "reading_history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    print(f"Created {len(books)} books, {len(students)} students, {len(history)} history records, {len(books)} cover images.")


if __name__ == "__main__":
    main()
