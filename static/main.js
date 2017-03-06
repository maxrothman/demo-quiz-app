'use strict'

function show_page(page) {
  if (page===null) {
    page = 1;
  }

  var req = new XMLHttpRequest();
  req.addEventListener("load", function() {
    var resp_json = JSON.parse(this.responseText);
    render(resp_json);
  });
  req.open("GET", '/question?page=' + page.toString());
  req.send();
}

function render(resp_json) {
  var question_el = document.querySelector('#question_list');
  while (question_el.firstChild) {
    question_el.removeChild(question_el.firstChild);
  }

  for (var qi = 0; qi < resp_json.questions.length; qi++) {
    var question_json = resp_json.questions[qi];

    var question_template = document.querySelector('#question_template').content.cloneNode(true);
    question_template.querySelector('.question_text').innerText = question_json.question;

    var answer_el = question_template.querySelector('.answers_list');
    
    var answers = question_json.distractors.concat([question_json.answer]);
    answers.sort(function(a, b){return 0.5 - Math.random()});
    
    for (var i = 0; i < answers.length; i++) {
      var answer_choice_template = document.querySelector('#answer_choice_template').content.cloneNode(true);
      answer_choice_template.querySelector('.answer_choice_label').innerText = answers[i];
      
      var radio = answer_choice_template.querySelector('.answer_choice_radio');
      radio.setAttribute('value', answers[i]);
      radio.dataset.correct = (answers[i] === question_json.answer);

      answer_el.appendChild(answer_choice_template);
    }

    question_el.appendChild(question_template);
  }
}

function check_answer(el) {
  var selected = Array.from(el.parentElement.querySelectorAll('.answer_choice_radio'))
    .filter(function(radio){return radio.checked})[0];
  var response_el = el.parentElement.querySelector('.question_check_answer_response');
  if (selected.dataset.correct === "true") {
    response_el.innerText = "Correct!";
    response_el.setAttribute('correct', false);
  } else {
    response_el.innerText = "Incorrect!";
    response_el.setAttribute('correct', true);
  }
}

function next_page() {
  cur_page += 1
  show_page(cur_page);
}

function prev_page() {
  cur_page -= 1;
  show_page(cur_page);
}

var cur_page = 1;
show_page(cur_page);