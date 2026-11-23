
const API_BASE_URL = "http://127.0.0.1:8000/api/benchmarks";

const apiRequest = async (url, options = {}) => {
    const response = await fetch(url, options);

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Something went wrong with the API request."
        );
    }

    return data;
};


// Get all available datasets
export const getAvailableDatasets = async () => {
    const data = await apiRequest(`${API_BASE_URL}/datasets`);
    return data.datasets;
};


// Get benchmark history
export const getBenchmarkHistory = async () => {
    const data = await apiRequest(`${API_BASE_URL}/`);
    return data.benchmarks;
};


// Get details of a particular benchmark
export const getBenchmarkDetails = async (id) => {
    return await apiRequest(`${API_BASE_URL}/${id}`);
};


// Start benchmark with selected configuration
export const startBenchmark = async (config = {}) => {

    const requestBody = {
        dataset_id: config.dataset_id || "breast_cancer",
        experiment_runs: config.experiment_runs ?? 5,
        inference_repeats: config.inference_repeats ?? 100
    };

    return await apiRequest(`${API_BASE_URL}/run`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
    });
};


// Get live benchmark progress
export const getBenchmarkStatus = async () => {
    return await apiRequest(`${API_BASE_URL}/run/status`);
};
