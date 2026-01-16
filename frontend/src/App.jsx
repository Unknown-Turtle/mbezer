import { useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js";

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [vizData, setVizData] = useState(null);
  const [method, setMethod] = useState("pca");

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus("");
      setVizData(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setStatus("Analyzing data...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/upload?method=${method}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } },
      );

      setVizData(response.data.points);
      setStatus(
        `Success! Visualizing ${response.data.points.length} points via ${method.toUpperCase()}`,
      );
    } catch (error) {
      console.error(error);
      setStatus("Error: Backend connection failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center p-8" style={{
      backgroundImage: `
        linear-gradient(rgba(156, 163, 175, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(156, 163, 175, 0.1) 1px, transparent 1px)
      `,
      backgroundSize: '20px 20px'
    }}>
      {/* Header */}
      <div className="w-full max-w-7xl mb-8 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-black">
          Mbezer
        </h1>
        <p className="text-sm text-gray-500 mt-1">3D Data Visualization Platform</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 w-full max-w-7xl h-[calc(100vh-180px)] lg:ml-auto lg:mr-16">
        {/* Left Panel: The 3D Plot */}
        <div className="lg:flex-1 bg-white overflow-hidden relative border-4 border-[#ff006e]" style={{ boxShadow: '8px 8px 0px rgba(0, 0, 0, 0.15)' }}>
          {!vizData ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <p className="text-sm font-medium">Upload data to generate a 3D embedding map</p>
              <p className="text-xs text-gray-400 mt-1">Visualize high-dimensional data in 3D space</p>
            </div>
          ) : (
            <Plot
              data={[
                {
                  x: vizData.map((p) => p.x),
                  y: vizData.map((p) => p.y),
                  z: vizData.map((p) => p.z),
                  mode: "markers",
                  type: "scatter3d",
                  text: vizData.map((p) => p.label),
                  marker: {
                    size: 5,
                    color: vizData.map((p) => p.cluster),
                    colorscale: [
                      [0, "#667eea"],
                      [0.33, "#00ff87"],
                      [0.66, "#b537ff"],
                      [1, "#ff006e"],
                    ],
                    opacity: 0.85,
                    line: {
                      color: "rgba(255, 255, 255, 0.3)",
                      width: 0.5,
                    },
                  },
                },
              ]}
              layout={{
                autosize: true,
                paper_bgcolor: "rgba(255,255,255,0)",
                plot_bgcolor: "rgba(255,255,255,0)",
                margin: { l: 0, r: 0, b: 0, t: 0 },
                scene: {
                  xaxis: {
                    color: "#9ca3af",
                    gridcolor: "rgba(156, 163, 175, 0.1)",
                    showbackground: false,
                  },
                  yaxis: {
                    color: "#9ca3af",
                    gridcolor: "rgba(156, 163, 175, 0.1)",
                    showbackground: false,
                  },
                  zaxis: {
                    color: "#9ca3af",
                    gridcolor: "rgba(156, 163, 175, 0.1)",
                    showbackground: false,
                  },
                  bgcolor: "rgba(255,255,255,0)",
                },
              }}
              style={{ width: "100%", height: "100%" }}
              config={{ responsive: true }}
            />
          )}
        </div>

        {/* Right Panel: Controls */}
        <div className="lg:w-80 flex flex-col gap-5">
          {/* Data Input Card */}
          <div className="bg-white p-6 border-4 border-[#ff006e]" style={{ boxShadow: '8px 8px 0px rgba(0, 0, 0, 0.15)' }}>
            <div className="flex items-center gap-2 mb-5">
              <h2 className="font-semibold text-gray-800">Data Input</h2>
            </div>

            <div className="relative group">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div className="border-2 border-dashed border-gray-200 p-8 text-center transition-all duration-300 group-hover:border-[#667eea] group-hover:bg-[#667eea]/5 cursor-pointer">
                <p className="text-sm font-medium text-gray-700 mb-1">
                  {file ? file.name : "Upload CSV File"}
                </p>
                <p className="text-xs text-gray-400">Click or drag to upload</p>
              </div>
            </div>
          </div>

          {/* Algorithm Selection Card */}
          <div className="bg-white p-6 border-4 border-[#ff006e]" style={{ boxShadow: '8px 8px 0px rgba(0, 0, 0, 0.15)' }}>
            <div className="flex items-center gap-2 mb-5">
              <h2 className="font-semibold text-gray-800">Algorithm</h2>
            </div>

            <div className="space-y-2 mb-5">
              {[
                { value: "pca", label: "PCA", desc: "Fastest / Linear" },
                { value: "umap", label: "UMAP", desc: "Best Structure" },
                { value: "tsne", label: "t-SNE", desc: "Best Clustering" },
              ].map((option) => (
                <label
                  key={option.value}
                  className={`block cursor-pointer p-3 transition-all duration-200 ${method === option.value
                    ? "bg-gradient-to-r from-[#667eea]/10 to-[#b537ff]/10 border-2 border-[#667eea]"
                    : "bg-white/50 border-2 border-transparent hover:bg-white/80"
                    }`}
                >
                  <input
                    type="radio"
                    name="method"
                    value={option.value}
                    checked={method === option.value}
                    onChange={(e) => setMethod(e.target.value)}
                    className="sr-only"
                  />
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-gray-800 text-sm">{option.label}</p>
                      <p className="text-xs text-gray-500">{option.desc}</p>
                    </div>
                    <div
                      className={`w-5 h-5 border-2 transition-all ${method === option.value
                        ? "border-[#667eea] bg-[#667eea]"
                        : "border-gray-300"
                        }`}
                    >
                      {method === option.value && (
                        <div className="w-full h-full bg-white scale-50" />
                      )}
                    </div>
                  </div>
                </label>
              ))}
            </div>

            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className={`w-full py-3.5 font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${!file || loading
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-gradient-to-r from-[#667eea] via-[#b537ff] to-[#ff006e] text-white hover:opacity-90"
                }`}
            >
              {loading ? "Processing..." : "Generate Map"}
            </button>

            {status && (
              <div className="mt-4 p-3 bg-gradient-to-r from-[#667eea]/10 to-[#b537ff]/10 border border-[#667eea]/20">
                <p className="text-xs text-gray-700 text-center">{status}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;