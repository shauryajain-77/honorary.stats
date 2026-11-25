// Speak.js - Screen 2
// Features: Record button with pulsing animation, text box fallback, Continue button, loading spinner

window.Speak = function Speak({ t, lang, initialText, onContinue, isLoading, errorMessage }) {
  const [isRecording, setIsRecording] = React.useState(false);
  const [text, setText] = React.useState(initialText || "");
  const [speechSupported, setSpeechSupported] = React.useState(false);
  const recognitionRef = React.useRef(null);

  React.useEffect(() => {
    // Check for browser speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      // Support English, Hindi, or Kannada in SpeechRecognition
      recognition.lang = lang === "kn" ? "kn-IN" : (lang === "hi" ? "hi-IN" : "en-IN");

      recognition.onresult = (event) => {
        let currentTranscript = "";
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript + " ";
        }
        setText(currentTranscript.trim());
      };

      recognition.onerror = (e) => {
        console.warn("Speech recognition notice:", e.error);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    }
  }, [lang]);

  const toggleRecording = () => {
    if (isRecording) {
      // Stop recording
      try {
        if (recognitionRef.current) {
          recognitionRef.current.stop();
        }
      } catch (e) {
        console.warn(e);
      }
      setIsRecording(false);
    } else {
      // Start recording
      setIsRecording(true);
      if (recognitionRef.current) {
        try {
          recognitionRef.current.lang = lang === "kn" ? "kn-IN" : (lang === "hi" ? "hi-IN" : "en-IN");
          recognitionRef.current.start();
        } catch (e) {
          console.warn("Speech API start notice:", e);
        }
      } else {
        // Fallback simulation for browsers without Web Speech
        if (!text) {
          const samplePhrase = lang === "kn"
            ? "ನಾನು 8 ವರ್ಷಗಳಿಂದ ಬಟ್ಟೆ ಹೊಲಿಯುತ್ತಿದ್ದೇನೆ. ಬ್ಲೌಸ್, ಸಲ್ವಾರ್ ಸೂಟ್ ಹೊಲಿಯುತ್ತೇನೆ ಮತ್ತು ಆಲ್ಟರೇಶನ್ ಮಾಡುತ್ತೇನೆ."
            : (lang === "hi" 
                ? "मैं 8 साल से दर्जी का काम कर रही हूँ। ब्लाउज, सलवार सूट सिलती हूँ और अल्टरेशन करती हूँ।" 
                : "I am a tailor with 8 years of experience. I stitch blouses, suits and do alterations.");
          
          let i = 0;
          const interval = setInterval(() => {
            i += 5;
            setText(samplePhrase.slice(0, i));
            if (i >= samplePhrase.length) {
              clearInterval(interval);
              setIsRecording(false);
            }
          }, 60);
        }
      }
    }
  };

  const handleContinue = () => {
    if (isRecording && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsRecording(false);
    }
    const fallbackText = lang === "kn"
      ? "ನಾನು 8 ವರ್ಷಗಳಿಂದ ಬಟ್ಟೆ ಹೊಲಿಯುತ್ತಿದ್ದೇನೆ. ಬ್ಲೌಸ್ ಮತ್ತು ಸಲ್ವಾರ್ ಸೂಟ್ ಹೊಲಿಯುತ್ತೇನೆ."
      : (lang === "hi" 
          ? "मैं 8 साल से कपड़े सिलती हूँ। ब्लाउज और सलवार सूट बनाना जानती हूँ।" 
          : "I have 8 years experience in tailoring, stitching clothes and alterations.");
    
    const finalContent = text.trim() || fallbackText;
    onContinue(finalContent);
  };

  return (
    <div className="main-content">
      {errorMessage && (
        <div className="error-box">
          <span>⚠️</span>
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="card text-center" style={{ marginBottom: "var(--space-md)" }}>
        <h2 style={{ fontSize: "var(--font-size-lg)", marginBottom: "var(--space-xs)" }}>
          {t.speakHeading}
        </h2>
        <p className="subheading" style={{ fontSize: "var(--font-size-sm)", marginBottom: "var(--space-md)" }}>
          {t.speakSubheading}
        </p>

        {/* Pulsing Voice Recording Area */}
        <div className="mic-hero-container" style={{ padding: "var(--space-sm) 0" }}>
          <div className="mic-pulse-wrapper">
            {isRecording && (
              <>
                <div className="pulse-ring"></div>
                <div className="pulse-ring-outer"></div>
              </>
            )}
            <button
              type="button"
              className="btn-mic-large"
              style={{
                background: isRecording
                  ? "linear-gradient(135deg, #E0482B, #C36145)"
                  : "linear-gradient(135deg, var(--accent-sage), #4D7656)",
                boxShadow: isRecording
                  ? "0 10px 24px rgba(224, 72, 43, 0.4)"
                  : "0 10px 24px rgba(94, 138, 104, 0.35)"
              }}
              onClick={toggleRecording}
              aria-label={isRecording ? t.recordingTapToStop : t.recordingTapToStart}
            >
              {isRecording ? (
                // Stop square icon
                <svg viewBox="0 0 24 24" style={{ width: 36, height: 36 }}>
                  <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
              ) : (
                // Microphone icon
                <svg viewBox="0 0 24 24">
                  <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                  <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
              )}
            </button>
          </div>

          <p style={{
            fontSize: "var(--font-size-base)",
            fontWeight: "700",
            color: isRecording ? "var(--accent-terracotta)" : "var(--text-charcoal)",
            margin: "var(--space-xs) 0"
          }}>
            {isRecording ? t.recordingActive : t.recordingTapToStart}
          </p>
          <p style={{ fontSize: "0.813rem", color: "var(--text-muted)" }}>
            {isRecording 
              ? t.recordingTapToStop 
              : (lang === "kn" 
                  ? "(ಮಾತನಾಡಲು ಮೈಕ್ ಒತ್ತಿ ಅಥವಾ ಕೆಳಗೆ ಟೈಪ್ ಮಾಡಿ)" 
                  : (lang === "hi" ? "(माइक दबाकर बोलें या नीचे लिखें)" : "(Tap mic to record or type below)"))}
          </p>
        </div>
      </div>

      {/* Textarea Fallback */}
      <div className="card" style={{ marginBottom: "var(--space-md)" }}>
        <div className="form-group" style={{ marginBottom: 0 }}>
          <label className="form-label" htmlFor="work-text-input">
            {t.textFallbackLabel}
          </label>
          <textarea
            id="work-text-input"
            className="textarea-text"
            rows="3"
            placeholder={t.textPlaceholder}
            value={text}
            onChange={(e) => setText(e.target.value)}
          ></textarea>
        </div>
      </div>

      {/* Continue Button or Loading Spinner */}
      {isLoading ? (
        <div className="spinner-container">
          <div className="spinner"></div>
          <p style={{ fontWeight: "600", color: "var(--accent-sage)" }}>
            {t.analyzingSkills}
          </p>
        </div>
      ) : (
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleContinue}
        >
          <span>{t.continueBtn}</span>
          <span>→</span>
        </button>
      )}
    </div>
  );
};
