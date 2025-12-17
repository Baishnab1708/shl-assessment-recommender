async function getRecommendations() {
  const queryInput = document.getElementById("query");
  const topKInput = document.getElementById("topK");
  const resultsDiv = document.getElementById("results");

  const query = queryInput.value.trim();

  let topK = Number(topKInput.value);

  if (Number.isNaN(topK) || topK < 1) {
    topK = 5;
  }

  if (topK > 10) {
    topK = 10;
  }

  resultsDiv.innerHTML = "";

  if (!query) {
    alert("Please enter a query");
    return;
  }

  resultsDiv.innerHTML = "<p>Loading recommendations...</p>";

  try {
    const API_BASE_URL = "https://shl-recomendation-system.onrender.com";

    const response = await fetch(`${API_BASE_URL}/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: query,
        top_k: topK
      })
    });

    if (!response.ok) {
      throw new Error("API request failed");
    }

    const data = await response.json();
    renderResults(data.recommended_assessments);

  } catch (error) {
    console.error(error);
    resultsDiv.innerHTML =
      "<p style='color:red'>Failed to fetch recommendations</p>";
  }
}

function renderResults(items) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";

  if (!items || items.length === 0) {
    resultsDiv.innerHTML = "<p>No recommendations found.</p>";
    return;
  }

  items.forEach(item => {
    const card = document.createElement("div");
    card.className = "result-card";

    card.innerHTML = `
      <h3>${item.name}</h3>
      <div class="meta">
        ${item.test_type} • ${item.duration ?? "N/A"} mins
      </div>
      <p>${item.description}</p>
      <div class="meta">
        Remote: ${item.remote_support ? "Yes" : "No"} |
        Adaptive: ${item.adaptive_support ? "Yes" : "No"}
      </div>
      <a href="${item.url}" target="_blank" rel="noopener noreferrer">
        View Assessment →
      </a>
    `;

    resultsDiv.appendChild(card);
  });
}

window.getRecommendations = getRecommendations;
