import React, { useState, useEffect } from 'react';
import { metricsAPI } from '../../services/api';
import './FormulaEditor.css';

const FormulaEditor = ({ onFormulaChange, initialFormula = '', variables = [] }) => {
    const [formula, setFormula] = useState(initialFormula);
    const [validationResult, setValidationResult] = useState(null);
    const [isValidating, setIsValidating] = useState(false);

    const operators = ['+', '-', '*', '/', '**', '(', ')'];
    const functions = ['sqrt', 'abs', 'log', 'exp', 'sin', 'cos', 'tan', 'min', 'max'];

    useEffect(() => {
        if (formula && variables.length > 0) {
            validateFormula();
        }
    }, [formula, variables]);

    const validateFormula = async () => {
        if (!formula || variables.length === 0) return;
        
        setIsValidating(true);
        try {
            const result = await metricsAPI.validateFormula(formula, variables);
            setValidationResult(result);
            if (onFormulaChange) {
                onFormulaChange(formula, result.is_valid);
            }
        } catch (error) {
            setValidationResult({ is_valid: false, error_message: 'Validation failed' });
        } finally {
            setIsValidating(false);
        }
    };

    const insertToken = (token) => {
        setFormula(prev => prev + token);
    };

    return (
        <div className="formula-editor">
            <div className="editor-header">
                <h3>Formula Builder</h3>
            </div>
            
            <div className="formula-input-section">
                <textarea
                    className="formula-input"
                    value={formula}
                    onChange={(e) => setFormula(e.target.value)}
                    placeholder="Enter formula (e.g., (revenue - cost) / revenue * 100)"
                    rows="4"
                />
                
                {validationResult && (
                    <div className={`validation-result ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
                        {validationResult.is_valid ? (
                            <span className="success">✓ Formula is valid</span>
                        ) : (
                            <span className="error">✗ {validationResult.error_message}</span>
                        )}
                    </div>
                )}
            </div>

            <div className="token-palette">
                <div className="token-group">
                    <h4>Variables</h4>
                    <div className="tokens">
                        {variables.map(variable => (
                            <button
                                key={variable}
                                className="token-btn variable"
                                onClick={() => insertToken(variable)}
                            >
                                {variable}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="token-group">
                    <h4>Operators</h4>
                    <div className="tokens">
                        {operators.map(op => (
                            <button
                                key={op}
                                className="token-btn operator"
                                onClick={() => insertToken(op)}
                            >
                                {op}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="token-group">
                    <h4>Functions</h4>
                    <div className="tokens">
                        {functions.map(func => (
                            <button
                                key={func}
                                className="token-btn function"
                                onClick={() => insertToken(`${func}()`)}
                            >
                                {func}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FormulaEditor;
