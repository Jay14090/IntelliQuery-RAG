import { useState } from 'react'
import axios from 'axios'
import { ReactFlow, Background, Controls, MarkerType } from '@xyflow/react'
import { motion } from 'framer-motion'
import { Play, RotateCcw, CheckCircle2, Clock } from 'lucide-react'

// Define the custom node
function CustomNode({ data }) {
  return (
    <div className={`react-flow__node-custom ${data.isActive ? 'active' : ''}`}>
      {data.label}
    </div>
  );
}

const nodeTypes = {
  custom: CustomNode,
};

// Initial static layout for LangGraph visualization
const initialNodes = [
  { id: '1', type: 'custom', position: { x: 50, y: 150 }, data: { label: 'Query Input', isActive: false } },
  { id: '2', type: 'custom', position: { x: 250, y: 150 }, data: { label: 'Anonymize', isActive: false } },
  { id: '3', type: 'custom', position: { x: 450, y: 50 }, data: { label: 'Plan', isActive: false } },
  { id: '4', type: 'custom', position: { x: 650, y: 50 }, data: { label: 'Retrieve', isActive: false } },
  { id: '5', type: 'custom', position: { x: 850, y: 50 }, data: { label: 'Reason', isActive: false } },
  { id: '6', type: 'custom', position: { x: 650, y: 250 }, data: { label: 'Synthesize', isActive: false } },
  { id: '7', type: 'custom', position: { x: 1050, y: 150 }, data: { label: 'Verify', isActive: false } }
];

const edgeParams = {
  type: 'smoothstep',
  animated: true,
  style: { stroke: '#818cf8', strokeWidth: 2 },
  markerEnd: { type: MarkerType.ArrowClosed, color: '#818cf8' },
};

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', ...edgeParams },
  { id: 'e2-3', source: '2', target: '3', ...edgeParams },
  { id: 'e3-4', source: '3', target: '4', ...edgeParams },
  { id: 'e4-5', source: '4', target: '5', ...edgeParams },
  { id: 'e5-7', source: '5', target: '7', ...edgeParams },
  { id: 'e3-6', source: '3', target: '6', ...edgeParams },
];

function App() {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('idle')
  const [response, setResponse] = useState(null)
  const [nodes, setNodes] = useState(initialNodes)

  const handleRun = async () => {
    if (!query.trim()) return;
    setStatus('running')
    setResponse(null)
    
    // Highlight nodes for visual effect
    setNodes(nds => nds.map(n => ({...n, data: {...n.data, isActive: n.id === '2'}})));
    
    try {
      const res = await axios.post('http://localhost:8000/api/query', { query })
      setResponse(res.data)
      setStatus('done')
      setNodes(nds => nds.map(n => ({...n, data: {...n.data, isActive: n.id === '7'}})));
    } catch (err) {
      console.error(err);
      setResponse({ final_response: "Error: " + (err.response?.data?.detail || err.message) })
      setStatus('idle')
      setNodes(initialNodes);
    }
  }

  const handleClear = () => {
    setQuery('')
    setStatus('idle')
    setResponse(null)
    setNodes(initialNodes)
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="glass-panel header-banner">
        <h1 className="gradient-text">IntelliQuery-RAG</h1>
        <p className="subtitle">Intelligent Graph-Orchestrated RAG Agent</p>
      </div>

      <div className="glass-panel">
        <div className="input-container">
          <textarea 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., Why did Duke Leto accept the posting to Arrakis despite knowing it was a trap?"
          />
          <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
            <button 
              className="primary" 
              onClick={handleRun}
              disabled={status === 'running'}
            >
              {status === 'running' ? <Clock size={18} className="animate-spin" style={{marginRight: '8px'}}/> : <Play size={18} style={{marginRight: '8px'}}/>}
              Run Agent
            </button>
            <button 
              className="secondary" 
              onClick={handleClear}
              style={{padding: '0.8rem', borderRadius: '16px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center'}}
            >
              <RotateCcw size={18} style={{marginRight: '8px'}}/> Clear
            </button>
          </div>
        </div>

        <div style={{marginTop: '2rem'}}>
          {status === 'idle' && <span className="status-badge status-idle"><Clock size={16}/> Idle</span>}
          {status === 'running' && <span className="status-badge status-running"><Clock size={16} style={{ animation: 'spin 2s linear infinite' }}/> Running...</span>}
          {status === 'done' && <span className="status-badge status-done"><CheckCircle2 size={16}/> Complete</span>}
        </div>
      </div>

      <div className="workflow-area">
        <ReactFlow 
          nodes={nodes} 
          edges={initialEdges} 
          nodeTypes={nodeTypes}
          fitView
        >
          <Background color="#334155" gap={16} />
          <Controls style={{backgroundColor: 'rgba(30,41,59,0.9)', fill: '#fff'}}/>
        </ReactFlow>
      </div>

      {response && (
        <motion.div 
          className="output-content"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <h3>💡 Final Answer</h3>
          <div style={{whiteSpace: 'pre-wrap', color: '#e2e8f0', fontSize: '1.1rem'}}>{response.final_response}</div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default App
