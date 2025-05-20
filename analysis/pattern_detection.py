"""
Pattern Detection Module - Session 8
-----------------------------------
This module implements detection of behavioral patterns from user tracking data.
It analyzes sequences of events and identifies meaningful patterns in user behavior.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/commitment')
engine = create_engine(DB_URL)

class PatternDetector:
    """Detects behavioral patterns in user tracking data."""
    
    def __init__(self, min_sequence_length=2, min_support=0.05, min_confidence=0.5):
        """
        Initialize the pattern detector.
        
        Args:
            min_sequence_length (int): Minimum length of sequences to consider
            min_support (float): Minimum support threshold for pattern detection
            min_confidence (float): Minimum confidence for pattern detection
        """
        self.min_sequence_length = min_sequence_length
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.engine = engine
        self.patterns = {}
        
    def get_user_sequences(self, days=30):
        """
        Retrieve user event sequences from the database.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            dict: Dictionary of user sequences by user_id
        """
        start_date = datetime.now() - timedelta(days=days)
        
        query = """
        SELECT 
            user_id,
            session_id,
            event_type,
            event_data,
            timestamp
        FROM 
            tracking_events
        WHERE 
            timestamp > :start_date
            AND user_id IS NOT NULL
        ORDER BY 
            user_id, session_id, timestamp
        """
        
        try:
            df = pd.read_sql(query, self.engine, params={'start_date': start_date})
            logger.info(f"Retrieved {len(df)} events for sequence analysis")
            
            if df.empty:
                return {}
                
            # Group by user and session
            sequences = defaultdict(list)
            
            for user_id, user_data in df.groupby('user_id'):
                for session_id, session_data in user_data.groupby('session_id'):
                    # Create a sequence of events for this session
                    if len(session_data) >= self.min_sequence_length:
                        session_sequence = []
                        
                        for _, event in session_data.iterrows():
                            # Add additional context from event_data if available
                            event_context = ""
                            if event['event_data']:
                                try:
                                    event_data = json.loads(event['event_data'])
                                    if isinstance(event_data, dict) and 'action' in event_data:
                                        event_context = f"_{event_data['action']}"
                                except:
                                    pass
                                    
                            event_signature = f"{event['event_type']}{event_context}"
                            session_sequence.append(event_signature)
                            
                        sequences[int(user_id)].append(session_sequence)
            
            return sequences
        except Exception as e:
            logger.error(f"Error retrieving user sequences: {e}")
            return {}
    
    def find_frequent_subsequences(self, sequences, min_support=None):
        """
        Find frequent subsequences in user sessions.
        
        Args:
            sequences (dict): Dictionary of user sequences
            min_support (float): Minimum support threshold
            
        Returns:
            dict: Dictionary of frequent patterns with their support
        """
        if not sequences:
            return {}
            
        if min_support is None:
            min_support = self.min_support
            
        # Flatten all sequences for analysis
        all_sequences = []
        for user_sequences in sequences.values():
            all_sequences.extend(user_sequences)
            
        total_sequences = len(all_sequences)
        min_count = max(2, int(min_support * total_sequences))
        
        logger.info(f"Looking for patterns in {total_sequences} sequences (min_count={min_count})")
        
        # Find all subsequences of length 2+
        subsequence_counts = Counter()
        
        for sequence in all_sequences:
            sequence_length = len(sequence)
            
            if sequence_length < self.min_sequence_length:
                continue
                
            # Generate all subsequences
            for start in range(sequence_length - self.min_sequence_length + 1):
                for length in range(self.min_sequence_length, min(sequence_length - start + 1, 6)):
                    subsequence = tuple(sequence[start:start+length])
                    subsequence_counts[subsequence] += 1
                    
        # Filter by minimum support
        frequent_patterns = {
            subseq: count 
            for subseq, count in subsequence_counts.items() 
            if count >= min_count
        }
        
        # Calculate support
        frequent_patterns_with_support = {
            subseq: {'count': count, 'support': count / total_sequences}
            for subseq, count in frequent_patterns.items()
        }
        
        logger.info(f"Found {len(frequent_patterns_with_support)} frequent patterns")
        return frequent_patterns_with_support
        
    def find_sequential_patterns(self, sequences):
        """
        Find sequential patterns in user behavior.
        
        Args:
            sequences (dict): Dictionary of user sequences
            
        Returns:
            list: List of detected patterns
        """
        frequent_patterns = self.find_frequent_subsequences(sequences)
        
        if not frequent_patterns:
            return []
            
        # Sort patterns by support
        sorted_patterns = sorted(
            frequent_patterns.items(),
            key=lambda x: x[1]['support'],
            reverse=True
        )
        
        patterns = []
        for pattern_seq, stats in sorted_patterns:
            pattern_str = " → ".join(pattern_seq)
            pattern = {
                'sequence': pattern_seq,
                'description': pattern_str,
                'support': stats['support'],
                'count': stats['count'],
                'length': len(pattern_seq)
            }
            patterns.append(pattern)
            
        return patterns
            
    def find_user_patterns(self, user_sequences, patterns):
        """
        Find which patterns apply to each user.
        
        Args:
            user_sequences (dict): Dictionary of user sequences
            patterns (list): List of detected patterns
            
        Returns:
            dict: Dictionary mapping users to patterns
        """
        user_patterns = defaultdict(list)
        
        for user_id, sequences in user_sequences.items():
            # Flatten user sequences
            flat_sequences = []
            for seq in sequences:
                flat_sequences.append(tuple(seq))
                
            # Check each pattern against user sequences
            for pattern in patterns:
                pattern_seq = pattern['sequence']
                matches = 0
                
                for seq in flat_sequences:
                    # Check if pattern is a subsequence
                    seq_str = " ".join(seq)
                    pattern_str = " ".join(pattern_seq)
                    
                    if pattern_str in seq_str:
                        matches += 1
                        
                if matches > 0:
                    strength = matches / len(sequences)
                    user_patterns[user_id].append({
                        'pattern_desc': pattern['description'],
                        'pattern_sequence': pattern_seq,
                        'matches': matches,
                        'strength': strength
                    })
                    
        return user_patterns
        
    def cluster_sequences(self, sequences):
        """
        Cluster similar sequences to find behavioral patterns.
        
        Args:
            sequences (dict): Dictionary of user sequences
            
        Returns:
            list: List of sequence clusters
        """
        if not sequences:
            return []
            
        # Flatten sequences
        flat_sequences = []
        sequence_users = []
        
        for user_id, user_sequences in sequences.items():
            for seq in user_sequences:
                seq_str = " ".join(seq)
                flat_sequences.append(seq_str)
                sequence_users.append(user_id)
                
        if len(flat_sequences) < 3:
            return []  # Need at least 3 sequences for meaningful clustering
            
        # Vectorize sequences
        vectorizer = TfidfVectorizer(ngram_range=(1, 3), min_df=2)
        X = vectorizer.fit_transform(flat_sequences)
        
        # Compute similarity matrix
        similarity_matrix = cosine_similarity(X)
        
        # Cluster sequences
        clustering = DBSCAN(eps=0.5, min_samples=2, metric='precomputed')
        distance_matrix = 1 - similarity_matrix
        labels = clustering.fit_predict(distance_matrix)
        
        # Organize results by cluster
        clusters = defaultdict(list)
        for i, (label, seq, user_id) in enumerate(zip(labels, flat_sequences, sequence_users)):
            if label >= 0:  # Ignore noise points (-1)
                clusters[label].append({
                    'sequence': seq,
                    'user_id': user_id,
                    'index': i
                })
                
        # Format clusters
        cluster_results = []
        for label, members in clusters.items():
            if len(members) >= 2:
                # Find the most representative sequence
                indices = [m['index'] for m in members]
                center_idx = np.argmax(np.sum(similarity_matrix[indices][:, indices], axis=1))
                representative = members[center_idx]['sequence']
                
                cluster_results.append({
                    'label': label,
                    'size': len(members),
                    'representative': representative,
                    'users': list(set(m['user_id'] for m in members))
                })
                
        return cluster_results
    
    def save_behavioral_patterns(self, patterns):
        """
        Save detected behavioral patterns to the database.
        
        Args:
            patterns (list): List of detected patterns
            
        Returns:
            dict: Dictionary mapping pattern descriptions to database IDs
        """
        pattern_ids = {}
        
        for i, pattern in enumerate(patterns):
            pattern_type = 'navigation'
            if any('click' in step or 'select' in step for step in pattern['sequence']):
                pattern_type = 'interaction'
            if any('purchase' in step or 'submit' in step for step in pattern['sequence']):
                pattern_type = 'conversion'
                
            # Create a name for the pattern
            pattern_name = f"Pattern {i+1}: {' → '.join(pattern['sequence'][:2])}"
            if len(pattern['sequence']) > 2:
                pattern_name += " → ..."
                
            # Insert or update pattern
            query = """
            INSERT INTO behavioral_patterns (name, description, pattern_type)
            VALUES (:name, :description, :pattern_type)
            ON CONFLICT (name) DO UPDATE 
            SET description = :description, pattern_type = :pattern_type
            RETURNING pattern_id
            """
            
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(
                        text(query), 
                        {
                            'name': pattern_name, 
                            'description': pattern['description'],
                            'pattern_type': pattern_type
                        }
                    )
                    pattern_id = result.fetchone()[0]
                    conn.commit()
                    pattern_ids[pattern['description']] = pattern_id
            except Exception as e:
                logger.error(f"Error saving pattern {pattern_name}: {e}")
                
        return pattern_ids
    
    def save_user_patterns(self, user_patterns, pattern_ids):
        """
        Save user pattern associations to the database.
        
        Args:
            user_patterns (dict): Dictionary mapping users to patterns
            pattern_ids (dict): Dictionary mapping pattern descriptions to database IDs
            
        Returns:
            int: Number of user-pattern associations saved
        """
        count = 0
        now = datetime.now()
        
        for user_id, patterns in user_patterns.items():
            for pattern in patterns:
                pattern_desc = pattern['pattern_desc']
                if pattern_desc not in pattern_ids:
                    continue
                    
                pattern_id = pattern_ids[pattern_desc]
                strength = pattern['strength']
                
                query = """
                INSERT INTO user_patterns 
                    (user_id, pattern_id, strength, first_observed, last_observed, observation_count)
                VALUES 
                    (:user_id, :pattern_id, :strength, :observed, :observed, 1)
                ON CONFLICT (user_id, pattern_id) 
                DO UPDATE SET 
                    strength = :strength,
                    last_observed = :observed,
                    observation_count = user_patterns.observation_count + 1
                """
                
                try:
                    with self.engine.connect() as conn:
                        conn.execute(
                            text(query), 
                            {
                                'user_id': user_id, 
                                'pattern_id': pattern_id,
                                'strength': strength,
                                'observed': now
                            }
                        )
                        conn.commit()
                    count += 1
                except Exception as e:
                    logger.error(f"Error saving user pattern for user {user_id}: {e}")
                    
        return count
    
    def run_detection(self):
        """
        Run the pattern detection pipeline.
        
        Returns:
            dict: Summary of the detection results
        """
        start_time = datetime.now()
        logger.info("Starting pattern detection pipeline")
        
        # Step 1: Get user sequences
        user_sequences = self.get_user_sequences(days=30)
        if not user_sequences:
            logger.warning("No sequences available for pattern detection")
            return {'status': 'completed', 'patterns_found': 0, 'message': 'No data available'}
            
        # Step 2: Find sequential patterns
        patterns = self.find_sequential_patterns(user_sequences)
        
        # Step 3: Cluster sequences (alternative approach)
        clusters = self.cluster_sequences(user_sequences)
        
        # Step 4: Find user-pattern associations
        user_patterns = self.find_user_patterns(user_sequences, patterns)
        
        # Step 5: Save patterns to the database
        pattern_ids = self.save_behavioral_patterns(patterns)
        
        # Step 6: Save user-pattern associations
        user_pattern_count = self.save_user_patterns(user_patterns, pattern_ids)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'status': 'completed',
            'users_analyzed': len(user_sequences),
            'patterns_found': len(patterns),
            'clusters_found': len(clusters),
            'user_pattern_associations': user_pattern_count,
            'processing_time_seconds': processing_time,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    detector = PatternDetector()
    results = detector.run_detection()
    print(json.dumps(results, indent=2))
