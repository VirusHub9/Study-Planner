# Run this Flask app (save as app.py)

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ---------------- BACKEND LOGIC ---------------- #

def smart_summarize_syllabus(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return ["Basics", "Core Concepts", "Advanced Topics"]

    summary = []
    for l in lines:
        if len(summary) < 12:
            summary.append(l[:80])
    return summary


def generate_study_plan(subject, syllabus_text, total_days):
    try:
        total_days = int(total_days)
        if total_days < 1 or total_days > 365:
            return {"error": "Days must be between 1–365"}, 400
    except:
        return {"error": "Invalid days"}, 400

    topics = smart_summarize_syllabus(syllabus_text)

    plan = []
    topic_index = 0

    for day in range(1, total_days + 1):
        if day % 5 == 0:
            plan.append({
                "day": day,
                "topic": "Revision + AI Assessment",
                "tasks": [
                    "Revise previous topics",
                    "Solve mixed problems",
                    "Focus weak areas"
                ]
            })
        else:
            topic = topics[topic_index % len(topics)]
            topic_index += 1

            plan.append({
                "day": day,
                "topic": topic,
                "tasks": [
                    f"Understand: {topic}",
                    "Create short notes",
                    "Practice questions"
                ]
            })

    return {"summary": topics, "plan": plan}, 200

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/plan', methods=['POST'])
def plan():
    data = request.form

    syllabus_text = data.get('syllabus', '')

    file = request.files.get('file')
    if file:
        try:
            content = file.read().decode('utf-8', errors='ignore')
            syllabus_text += "\n" + content
        except:
            pass

    result, status = generate_study_plan(
        data.get('subject'),
        syllabus_text,
        data.get('days')
    )

    return jsonify(result), status

# ---------------- FRONTEND ---------------- #

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Study Planner Pro</title>

<style>
*{box-sizing:border-box}
body {
    font-family: system-ui;
    margin: 0;
    background: #0f172a;
    color: white;
}

.container{
    display:flex;
    min-height:100vh;
}

.sidebar{
    width:260px;
    background:#020617;
    padding:15px;
    overflow:auto;
    transition:0.3s;
}

.main{
    flex:1;
    padding:20px;
}

input, textarea {
    width:100%;
    padding:12px;
    margin:8px 0;
    border-radius:10px;
    border:none;
    background:#1e293b;
    color:white;
}

button{
    background:#3b82f6;
    border:none;
    padding:12px;
    border-radius:10px;
    color:white;
    font-weight:600;
    cursor:pointer;
    transition:0.2s;
}

button:hover{
    transform:scale(1.03);
}

.card{
    background:#1e293b;
    padding:15px;
    margin:10px 0;
    border-radius:12px;
    animation:fadeIn 0.4s ease;
}

.summary{
    background:#020617;
    padding:15px;
    border-radius:12px;
    margin-bottom:15px;
}

.history-item{
    padding:10px;
    background:#1e293b;
    margin:5px 0;
    border-radius:8px;
    cursor:pointer;
}

.topbar{
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap:10px;
}

/* MOBILE RESPONSIVE */
@media(max-width:768px){
    .container{
        flex-direction:column;
    }

    .sidebar{
        width:100%;
        order:2;
    }

    .main{
        order:1;
    }
}

@keyframes fadeIn{
    from{opacity:0; transform:translateY(10px)}
    to{opacity:1; transform:translateY(0)}
}
</style>
</head>
<body>

<div class="container">

<div class="sidebar">
<h3>🕘 History</h3>
<div id="history"></div>
<button onclick="clearAll()" style="background:#ef4444;margin-top:10px;width:100%">Clear All</button>
</div>

<div class="main">
<div class="topbar">
<h2>🧠 AI Study Planner</h2>
<button onclick="newChat()" style="background:#10b981">+ New</button>
</div>

<input id="subject" placeholder="Subject">
<textarea id="syllabus" rows="4" placeholder="Paste syllabus"></textarea>
<input type="file" id="file">
<input id="days" type="number" placeholder="Days">

<button onclick="generate()">Generate Plan</button>

<div id="output"></div>
</div>

</div>

<script>
let history = JSON.parse(localStorage.getItem('plans') || '[]');
renderHistory();

async function generate(){
    let formData = new FormData();
    let subject = document.getElementById('subject').value;

    formData.append('subject', subject);
    formData.append('syllabus', document.getElementById('syllabus').value);
    formData.append('days', document.getElementById('days').value);

    let file = document.getElementById('file').files[0];
    if(file) formData.append('file', file);

    let res = await fetch('/plan', {method:'POST', body:formData});
    let data = await res.json();

    display(data);

    history.unshift({subject, data});
    localStorage.setItem('plans', JSON.stringify(history));
    renderHistory();
}

function display(data){
    if(data.error){
        document.getElementById('output').innerHTML = `<div class='card'>${data.error}</div>`;
        return;
    }

    let html = `<div class='summary'><h3>Summary</h3>${data.summary.map(s=>`<div>${s}</div>`).join('')}</div>`;

    html += data.plan.map(d=>`
        <div class='card'>
        <h3>Day ${d.day}: ${d.topic}</h3>
        <ul>${d.tasks.map(t=>`<li>${t}</li>`).join('')}</ul>
        </div>
    `).join('');

    document.getElementById('output').innerHTML = html;
}

function renderHistory(){
    document.getElementById('history').innerHTML = history.map((h,i)=>
        `<div class='history-item' onclick='loadHistory(${i})'>${h.subject || 'Untitled'}</div>`
    ).join('');
}

function loadHistory(i){
    display(history[i].data);
}

function newChat(){
    document.getElementById('subject').value = '';
    document.getElementById('syllabus').value = '';
    document.getElementById('days').value = '';
    document.getElementById('file').value = '';
    document.getElementById('output').innerHTML = '';
}

function clearAll(){
    localStorage.removeItem('plans');
    history = [];
    renderHistory();
    newChat();
}
</script>

</body>
</html>
"""

if __name__ == '__main__':
    app.run()
