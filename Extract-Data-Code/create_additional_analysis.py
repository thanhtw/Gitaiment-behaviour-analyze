"""
Additional Analysis Data Export
===============================
Creates additional CSV files for specific analyses:
1. Correlation matrix
2. Player segments
"""

import pandas as pd
import numpy as np

def create_correlation_matrix(data_dir):
    """Create correlation matrix for key variables"""
    df = pd.read_csv(f"{data_dir}/analysis_spss_ready.csv")
    
    # Key variables for correlation
    corr_vars = [
        'HelpRatio', 'HintRatio', 'AnswerRatio',
        'FailureRate', 'ActionSuccessRate',
        'ManualOpens', 'LeaderboardChecks',
        'GameProgress', 'TotalScore', 'StagesCleared',
        'PerfectRatio', 'PlayTimeMinutes', 'QuestsCompleted'
    ]
    
    # Filter to existing columns
    existing_vars = [v for v in corr_vars if v in df.columns]
    
    # Calculate correlation matrix
    corr_matrix = df[existing_vars].corr()
    
    # Export
    corr_matrix.to_csv(f"{data_dir}/analysis_correlation_matrix.csv", encoding='utf-8-sig')
    print(f"Exported: analysis_correlation_matrix.csv")
    print(f"\nCorrelation Matrix (Key Variables):\n")
    print(corr_matrix.round(3).to_string())
    
    return corr_matrix

def create_player_segments(data_dir):
    """Create player segments for analysis"""
    df = pd.read_csv(f"{data_dir}/analysis_spss_ready.csv")
    
    # Create segments based on multiple criteria
    segments = []
    
    for _, row in df.iterrows():
        segment = {}
        segment['ID'] = row['ID']
        
        # Performance Level
        if row['GameProgress'] >= 80:
            segment['PerformanceLevel'] = 'High Performer'
            segment['PerformanceLevelCode'] = 3
        elif row['GameProgress'] >= 40:
            segment['PerformanceLevel'] = 'Medium Performer'
            segment['PerformanceLevelCode'] = 2
        else:
            segment['PerformanceLevel'] = 'Low Performer'
            segment['PerformanceLevelCode'] = 1
        
        # Learning Style (based on help usage)
        help_ratio = row.get('HelpRatio', 0)
        if help_ratio <= 0.05:
            segment['LearningStyle'] = 'Independent'
            segment['LearningStyleCode'] = 1
        elif help_ratio <= 0.15:
            segment['LearningStyle'] = 'Self-Reliant'
            segment['LearningStyleCode'] = 2
        else:
            segment['LearningStyle'] = 'Help-Seeking'
            segment['LearningStyleCode'] = 3
        
        # Engagement Level
        events = row.get('TotalEvents', 0)
        if events >= 500:
            segment['EngagementLevel'] = 'High Engagement'
            segment['EngagementLevelCode'] = 3
        elif events >= 100:
            segment['EngagementLevel'] = 'Medium Engagement'
            segment['EngagementLevelCode'] = 2
        else:
            segment['EngagementLevel'] = 'Low Engagement'
            segment['EngagementLevelCode'] = 1
        
        # Error Tendency
        failure_rate = row.get('FailureRate', 0)
        if failure_rate <= 0.02:
            segment['ErrorTendency'] = 'Low Error'
            segment['ErrorTendencyCode'] = 1
        elif failure_rate <= 0.05:
            segment['ErrorTendency'] = 'Medium Error'
            segment['ErrorTendencyCode'] = 2
        else:
            segment['ErrorTendency'] = 'High Error'
            segment['ErrorTendencyCode'] = 3
        
        # Resource Usage
        manual = row.get('ManualOpens', 0)
        leaderboard = row.get('LeaderboardChecks', 0)
        if manual >= 5 and leaderboard >= 10:
            segment['ResourceUsage'] = 'Active Explorer'
            segment['ResourceUsageCode'] = 3
        elif manual >= 1 or leaderboard >= 3:
            segment['ResourceUsage'] = 'Occasional User'
            segment['ResourceUsageCode'] = 2
        else:
            segment['ResourceUsage'] = 'Minimal User'
            segment['ResourceUsageCode'] = 1
        
        # Combined Segment (Performance + Learning Style)
        segment['CombinedSegment'] = f"{segment['PerformanceLevel']} / {segment['LearningStyle']}"
        
        # Add raw values for reference
        segment['GameProgress'] = row.get('GameProgress', 0)
        segment['HelpRatio'] = round(row.get('HelpRatio', 0), 3)
        segment['TotalEvents'] = row.get('TotalEvents', 0)
        segment['FailureRate'] = round(row.get('FailureRate', 0), 4)
        segment['TotalScore'] = row.get('TotalScore', 0)
        
        segments.append(segment)
    
    segment_df = pd.DataFrame(segments)
    segment_df.to_csv(f"{data_dir}/analysis_player_segments.csv", index=False, encoding='utf-8-sig')
    print(f"\nExported: analysis_player_segments.csv")
    
    # Print segment summary
    print("\n" + "=" * 60)
    print("PLAYER SEGMENT SUMMARY")
    print("=" * 60)
    
    print("\nPerformance Level Distribution:")
    print(segment_df['PerformanceLevel'].value_counts().to_string())
    
    print("\nLearning Style Distribution:")
    print(segment_df['LearningStyle'].value_counts().to_string())
    
    print("\nEngagement Level Distribution:")
    print(segment_df['EngagementLevel'].value_counts().to_string())
    
    print("\nCombined Segment Distribution:")
    print(segment_df['CombinedSegment'].value_counts().to_string())
    
    return segment_df

def main():
    data_dir = "."
    
    print("=" * 60)
    print("CREATING ADDITIONAL ANALYSIS FILES")
    print("=" * 60)
    
    # Create correlation matrix
    corr_matrix = create_correlation_matrix(data_dir)
    
    # Create player segments
    segment_df = create_player_segments(data_dir)
    
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
