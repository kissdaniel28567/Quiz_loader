"use strict";

const app = document.getElementById("app");
const state = { datasets: [], dataset: null, index: 0, records: [], phase: "answer" };

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function multiline(node, text) {
  String(text).split("\n").forEach((line, index) => {
    if (index) node.append(document.createElement("br"));
    node.append(document.createTextNode(line));
  });
  return node;
}

function button(text, className, action) {
  const node = element("button", `btn ${className}`, text);
  node.type = "button";
  node.addEventListener("click", action);
  return node;
}

function addRules(header) {
  const rules = element("div", "rules");
  rules.append(element("strong", "", "Exam Scoring System:"));
  const list = element("ul");
  [
    "Each question has multiple statements (at least one is true).",
    "Full score (1.0 pt): Select all true statements and only those.",
    "Half score (0.5 pt): Exactly one mistake (1 missed correct OR 1 chosen incorrect).",
    "Zero score (0.0 pt): Two or more mistakes.",
  ].forEach((text) => list.append(element("li", "", text)));
  rules.append(list);
  header.append(rules);
}

function renderHome() {
  state.dataset = null;
  const header = element("header");
  header.append(element("h1", "", "Quiz loader"));
  header.append(element("p", "subtitle", "Choose a dataset on this page, then try the quiz."));
  addRules(header);

  const section = element("section");
  section.append(element("h2", "section-title", "Datasets"));
  section.append(element("p", "subtitle section-intro", "Select a dataset, then try the quiz."));
  const list = element("div", "dataset-list");
  if (!state.datasets.length) {
    section.append(element("p", "empty", "No datasets are available."));
  } else {
    state.datasets.forEach((dataset, index) => {
      const card = element("label", "question-card dataset-card");
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "dataset";
      radio.value = dataset.slug;
      radio.checked = index === 0;
      const details = document.createElement("span");
      details.append(multiline(element("h2"), dataset.title));
      if (dataset.subtitle) details.append(multiline(element("p", "subtitle"), dataset.subtitle));
      const count = dataset.question_count;
      details.append(element(
        "p",
        "meta",
        `${count} ${count === 1 ? "question" : "questions"} · ${dataset.slug}.json`,
      ));
      card.append(radio, details);
      list.append(card);
    });
    section.append(list);
    section.append(element("p", "upload-help",
      "To add or replace a quiz, add its JSON file to the repository's datasets/ folder and publish again."));
    const controls = element("div", "btn-container");
    controls.append(button("Try quiz", "btn-submit", () => {
      const selected = app.querySelector('input[name="dataset"]:checked');
      const dataset = state.datasets.find((item) => item.slug === selected?.value);
      if (dataset) startQuiz(dataset);
    }));
    section.append(controls);
  }
  app.replaceChildren(header, section);
}

async function startQuiz(summary) {
  try {
    const response = await fetch(`datasets/${encodeURIComponent(summary.slug)}.json`);
    if (!response.ok) throw new Error(`Could not load ${summary.slug}.json (HTTP ${response.status}).`);
    state.dataset = await response.json();
    state.index = 0;
    state.records = [];
    state.phase = "answer";
    renderQuestion();
  } catch (error) {
    showError(error.message);
  }
}

function showError(message) {
  const notice = element("div", "flash flash-err", message);
  app.prepend(notice);
}

function renderQuestion() {
  const dataset = state.dataset;
  const question = dataset.questions[state.index];
  const header = element("header");
  const back = element("p", "back-link");
  const homeLink = element("a", "", "Change dataset");
  homeLink.href = "#";
  homeLink.addEventListener("click", (event) => {
    event.preventDefault();
    renderHome();
  });
  back.append(homeLink);
  header.append(back, multiline(element("h1"), dataset.title));
  if (dataset.subtitle) header.append(multiline(element("p", "subtitle"), dataset.subtitle));
  addRules(header);

  const main = element("section");
  const progress = element("div", "progress");
  const shown = state.index + 1;
  const percent = Math.round(shown / dataset.questions.length * 100);
  const label = element("div", "progress-label");
  label.append(element("span", "", `Question ${shown} of ${dataset.questions.length}`));
  label.append(element("span", "", `${percent}%`));
  const track = element("div", "progress-track");
  const fill = element("div", "progress-fill");
  fill.style.width = `${percent}%`;
  track.append(fill);
  progress.append(label, track);
  main.append(progress);

  const card = element("article", "question-card");
  const title = element("div", "question-title");
  title.append(multiline(element("span"), question.title));
  if (state.phase === "revealed") {
    const result = state.records[state.index];
    const css = result.points === 1 ? "score-good" : result.points === 0.5 ? "score-mid" : "score-bad";
    const noun = result.mistakes === 1 ? "mistake" : "mistakes";
    title.append(element("span", `question-score ${css}`,
      `${result.points.toFixed(1)} / 1.0 pt (${result.mistakes} ${noun})`));
  }
  card.append(title, multiline(element("p", "question-text"), question.text));

  const options = element("div", "options-list");
  question.options.forEach((option) => {
    const row = element("label", "option-label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = option.id;
    checkbox.disabled = state.phase === "revealed";
    const text = multiline(element("span"), option.text);
    text.prepend(element("strong", "", `${option.id}. `));
    if (state.phase === "revealed") {
      const result = state.records[state.index];
      if (result.correct.includes(option.id)) row.classList.add("correct-opt");
      else if (result.selected.includes(option.id)) row.classList.add("wrong-opt");
      checkbox.checked = result.selected.includes(option.id);
    }
    row.append(checkbox, text);
    options.append(row);
  });
  card.append(options);
  if (state.phase === "revealed") {
    const explanation = multiline(element(
      "div",
      `explanation ${state.records[state.index].points === 1 ? "good" : "neutral"}`,
    ), question.explanation || "No explanation provided.");
    explanation.prepend(element("strong", "", "Explanation: "));
    card.append(explanation);
  }
  main.append(card);

  const controls = element("div", "btn-container");
  if (state.phase === "answer") {
    controls.append(button("Validate", "btn-submit", () => {
      const selected = [...app.querySelectorAll(".options-list input:checked")].map((input) => input.value);
      const correct = new Set(question.correct);
      const chosen = new Set(selected);
      const mistakes = [...chosen].filter((id) => !correct.has(id)).length
        + [...correct].filter((id) => !chosen.has(id)).length;
      state.records[state.index] = {
        selected,
        correct: [...correct],
        mistakes,
        points: mistakes === 0 ? 1 : mistakes === 1 ? 0.5 : 0,
      };
      state.phase = "revealed";
      renderQuestion();
    }));
  } else {
    controls.append(button("Next", "btn-submit", () => {
      state.index += 1;
      if (state.index === dataset.questions.length) renderSummary();
      else {
        state.phase = "answer";
        renderQuestion();
      }
    }));
  }
  main.append(controls);
  app.replaceChildren(header, main);
}

function renderSummary() {
  const dataset = state.dataset;
  const total = state.records.reduce((sum, record) => sum + record.points, 0);
  const full = state.records.filter((record) => record.points === 1).length;
  const half = state.records.filter((record) => record.points === 0.5).length;
  const wrong = state.records.filter((record) => record.points === 0).length;
  const header = element("header");
  const back = element("p", "back-link");
  const homeLink = element("a", "", "Change dataset");
  homeLink.href = "#";
  homeLink.addEventListener("click", (event) => {
    event.preventDefault();
    renderHome();
  });
  back.append(homeLink);
  header.append(back, multiline(element("h1"), dataset.title));
  const banner = element("div", "score-banner");
  banner.append(element("p", "", "Your result"));
  banner.append(element("h2", "", `${total.toFixed(1)} / ${state.records.length}`));
  banner.append(element("p", "score-percent",
    `Score: ${state.records.length ? (total / state.records.length * 100).toFixed(1) : "0.0"}%`));
  const stats = element("div", "stat-row");
  [[full, "Fully correct"], [half, "Half credit"], [wrong, "Wrong"]].forEach(([count, label]) => {
    const stat = element("div", "stat");
    stat.append(element("strong", "", String(count)), element("span", "", label));
    stats.append(stat);
  });
  banner.append(stats);

  const filterLabel = element("label", "wrong-filter", "Show only wrong");
  const filter = document.createElement("input");
  filter.type = "checkbox";
  filter.id = "showWrongOnly";
  filterLabel.prepend(filter);
  const empty = element("p", "empty", "Nothing to show. Every question was fully correct.");
  empty.hidden = true;
  const cards = element("section");
  const renderedCards = [];
  dataset.questions.forEach((question, index) => {
    const record = state.records[index];
    const card = element("article", "question-card");
    card.dataset.perfect = record.points === 1 ? "1" : "0";
    const title = element("div", "question-title");
    title.append(multiline(element("span"), question.title));
    const css = record.points === 1 ? "score-good" : record.points === 0.5 ? "score-mid" : "score-bad";
    const noun = record.mistakes === 1 ? "mistake" : "mistakes";
    title.append(element("span", `question-score ${css}`,
      `${record.points.toFixed(1)} / 1.0 pt (${record.mistakes} ${noun})`));
    card.append(title, multiline(element("p", "question-text"), question.text));
    const options = element("div", "options-list");
    question.options.forEach((option) => {
      const row = element("label", "option-label");
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.disabled = true;
      checkbox.checked = record.selected.includes(option.id);
      if (record.correct.includes(option.id)) row.classList.add("correct-opt");
      else if (checkbox.checked) row.classList.add("wrong-opt");
      const text = multiline(element("span"), option.text);
      text.prepend(element("strong", "", `${option.id}. `));
      row.append(checkbox, text);
      options.append(row);
    });
    card.append(options);
    const explanation = multiline(element(
      "div",
      `explanation ${record.points === 1 ? "good" : "neutral"}`,
    ), question.explanation || "No explanation provided.");
    explanation.prepend(element("strong", "", "Explanation: "));
    card.append(explanation);
    cards.append(card);
    renderedCards.push(card);
  });
  filter.addEventListener("change", () => {
    renderedCards.forEach((card) => {
      card.hidden = filter.checked && card.dataset.perfect === "1";
    });
    empty.hidden = !(filter.checked && wrong + half === 0);
  });
  const controls = element("div", "btn-container");
  controls.append(
    button("Retake Quiz", "btn-reset", () => {
      state.index = 0;
      state.records = [];
      state.phase = "answer";
      renderQuestion();
    }),
    button("Change dataset", "btn-secondary", renderHome),
  );
  app.replaceChildren(header, banner, filterLabel, empty, cards, controls);
}

async function main() {
  try {
    const response = await fetch("datasets/index.json");
    if (!response.ok) throw new Error(`Could not load the quiz list (HTTP ${response.status}).`);
    state.datasets = await response.json();
    renderHome();
  } catch (error) {
    app.replaceChildren(element("p", "flash flash-err", error.message));
  }
}

main();
