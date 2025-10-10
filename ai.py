"""
ml_ai.py - Machine Learning AI untuk Voice Robot
Menggunakan Scikit-learn untuk text classification
"""

import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from typing import Optional, List, Tuple

class MLRobotAI:
    """
    Machine Learning AI menggunakan:
    - TF-IDF untuk feature extraction
    - Naive Bayes untuk classification
    """
    
    def __init__(self):
        self.pipeline = None
        self.command_map = {
            "light_on": "L13:1:5",
            "light_off": "L13:0:0",
            "move_forward": "MF:90:1",
            "move_backward": "MB:90:1",
            "move_left": "ML:90:1",
            "move_right": "MR:90:1",
            "stop": "MS:0:0",
            "read_temperature": "TR",
            "read_humidity": "HR",
            "alarm": "S1000:1;S2000:1;S1000:1",
            "beep": "S1000:1",
        }
        
        self.is_trained = False
    
    def create_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Create training dataset
        Returns: (texts, labels)
        """
        training_data = [
            # LIGHT ON
            ("nyalakan lampu", "light_on"),
            ("hidupin lampunya", "light_on"),
            ("tolong nyalakan", "light_on"),
            ("lampu hidup", "light_on"),
            ("terangin dong", "light_on"),
            ("on lampu", "light_on"),
            ("aktifkan cahaya", "light_on"),
            
            # LIGHT OFF
            ("matikan lampu", "light_off"),
            ("lampu mati", "light_off"),
            ("padamkan", "light_off"),
            ("off lampunya", "light_off"),
            ("matiin deh", "light_off"),
            ("gelapin", "light_off"),
            
            # FORWARD
            ("maju", "move_forward"),
            ("jalan kedepan", "move_forward"),
            ("maju robot", "move_forward"),
            ("kedepan", "move_forward"),
            ("forward", "move_forward"),
            ("maju pelan", "move_forward"),
            ("majuin dong", "move_forward"),
            
            # BACKWARD
            ("mundur", "move_backward"),
            ("kebelakang", "move_backward"),
            ("mundur robot", "move_backward"),
            ("back", "move_backward"),
            ("mundurin", "move_backward"),
            
            # LEFT
            ("kiri", "move_left"),
            ("belok kiri", "move_left"),
            ("ke kiri", "move_left"),
            ("turn left", "move_left"),
            ("belok ke kiri", "move_left"),
            
            # RIGHT
            ("kanan", "move_right"),
            ("belok kanan", "move_right"),
            ("ke kanan", "move_right"),
            ("turn right", "move_right"),
            ("belok ke kanan", "move_right"),
            
            # STOP
            ("berhenti", "stop"),
            ("stop", "stop"),
            ("diam", "stop"),
            ("berhenti robot", "stop"),
            ("jangan jalan", "stop"),
            ("semuanya diammm", "stop"),
            
            # TEMPERATURE
            ("suhu", "read_temperature"),
            ("cek suhu", "read_temperature"),
            ("berapa suhu", "read_temperature"),
            ("temperature", "read_temperature"),
            ("panas berapa", "read_temperature"),
            
            # HUMIDITY
            ("kelembaban", "read_humidity"),
            ("cek kelembaban", "read_humidity"),
            ("berapa kelembapan", "read_humidity"),
            ("humidity", "read_humidity"),
            ("lembab berapa", "read_humidity"),
            
            # ALARM
            ("alarm", "alarm"),
            ("bunyi alarm", "alarm"),
            ("aktifkan alarm", "alarm"),
            ("sirine", "alarm"),
            
            # BEEP
            ("bunyi", "beep"),
            ("beep", "beep"),
            ("bel", "beep"),
            ("bunyiin", "beep"),
        ]
        
        texts = [text for text, _ in training_data]
        labels = [label for _, label in training_data]
        
        return texts, labels
    
    def train(self, save_model: bool = True):
        """Train the ML model"""
        print("🧠 Training ML model...")
        
        # Get training data
        texts, labels = self.create_training_data()
        
        # Create pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                ngram_range=(1, 2),  # Unigrams and bigrams
                max_features=100,
                lowercase=True,
                strip_accents='unicode'
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Train
        self.pipeline.fit(texts, labels)
        self.is_trained = True
        
        # Calculate accuracy
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        self.pipeline.fit(X_train, y_train)
        accuracy = self.pipeline.score(X_test, y_test)
        
        print(f"✅ Model trained! Accuracy: {accuracy*100:.1f}%")
        
        # Save model
        if save_model:
            with open('robot_ml_model.pkl', 'wb') as f:
                pickle.dump(self.pipeline, f)
            print("💾 Model saved to robot_ml_model.pkl")
    
    def load_model(self, filename: str = 'robot_ml_model.pkl'):
        """Load trained model"""
        try:
            with open(filename, 'rb') as f:
                self.pipeline = pickle.load(f)
            self.is_trained = True
            print(f"✅ Model loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"⚠️ Model file not found: {filename}")
            return False
    
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict command label and confidence
        Returns: (label, confidence)
        """
        if not self.is_trained:
            raise Exception("Model not trained! Call train() or load_model() first.")
        
        # Predict
        label = self.pipeline.predict([text])[0]
        
        # Get probability
        probas = self.pipeline.predict_proba([text])[0]
        confidence = max(probas)
        
        return label, confidence
    
    def process_command(self, text: str, threshold: float = 0.5, verbose: bool = True) -> Optional[str]:
        """
        Process command using ML
        threshold: minimum confidence (0.0-1.0)
        """
        if not text:
            return None
        
        if not self.is_trained:
            print("⚠️ Model not trained! Training now...")
            self.train()
        
        if verbose:
            print(f"\n🤖 ML Processing: '{text}'")
        
        # Predict
        label, confidence = self.predict(text)
        
        if verbose:
            print(f"🎯 Predicted: {label} (confidence: {confidence*100:.1f}%)")
        
        # Check confidence threshold
        if confidence < threshold:
            if verbose:
                print(f"⚠️ Low confidence ({confidence*100:.1f}% < {threshold*100:.1f}%)")
            return None
        
        # Get Arduino command
        command = self.command_map.get(label)
        
        if verbose:
            if command:
                print(f"✅ Command: {command}")
            else:
                print(f"❌ No command mapping for label: {label}")
        
        return command
    
    def get_all_predictions(self, text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Get top-k predictions with probabilities"""
        if not self.is_trained:
            return []
        
        # Get all probabilities
        probas = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_
        
        # Sort by probability
        indices = np.argsort(probas)[::-1][:top_k]
        
        results = [(classes[i], probas[i]) for i in indices]
        return results


# ===============================================
# TESTING & DEMO
# ===============================================

def test_ml_ai():
    """Test ML AI"""
    ai = MLRobotAI()
    
    print("="*60)
    print("🧪 TESTING ML AI")
    print("="*60 + "\n")
    
    # Train model
    ai.train()
    
    print("\n" + "="*60)
    print("📊 TESTING PREDICTIONS")
    print("="*60)
    
    test_cases = [
        "nyalakan lampunya dong",
        "tolong matikan",
        "robot maju yuk",
        "mundur pelan pelan",
        "belok kiri sekarang",
        "stop robot",
        "berapa suhu sekarang",
        "cek kelembaban",
        "bunyikan alarm",
        "halo robot",  # Should have low confidence
    ]
    
    for text in test_cases:
        # Get command
        cmd = ai.process_command(text, threshold=0.3, verbose=True)
        
        # Get top 3 predictions
        top_preds = ai.get_all_predictions(text, top_k=3)
        print("📊 Top 3 predictions:")
        for i, (label, prob) in enumerate(top_preds, 1):
            print(f"   {i}. {label}: {prob*100:.1f}%")
        
        print("-"*60)


if __name__ == "__main__":
    # Run test
    test_ml_ai()
    
    # Interactive mode
    print("\n" + "="*60)
    print("🎤 INTERACTIVE MODE")
    print("="*60)
    print("Ketik perintah atau 'quit' untuk keluar\n")
    
    ai = MLRobotAI()
    
    # Load or train model
    if not ai.load_model():
        ai.train()
    
    while True:
        try:
            text = input(">>> Perintah: ").strip()
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            cmd = ai.process_command(text, threshold=0.4)
            if cmd:
                print(f"✅ Will send to Arduino: {cmd}\n")
            else:
                print("❌ Command not recognized or low confidence\n")
                
        except KeyboardInterrupt:
            break
    
    print("\n👋 Selesai!")