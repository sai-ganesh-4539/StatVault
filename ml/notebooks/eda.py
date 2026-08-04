#importations

import pandas as pd
import numpy as np
#ensures safer path handling
from pathlib import Path
import json
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

#class for doing data analysis
class DataQualityAnalyzer:
    def __init__(self,base_path:str="."):
        self.base_path = Path(base_path).resolve()
        self.raw_data_path = self.base_path / "data" / "raw"
        self.reports_path = self.base_path / "data" / "reports"
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.datasets = {}
        self.reports = {}

    
    def load_datasets(self) -> None:
        dataset_paths = {
            # FIFA 22 player dataset
            "fifa22_players": self.raw_data_path / "fifa22" / "players_22.csv",
            # FIFA 24 player dataset
            "fifa24_players": self.raw_data_path / "fifa24-25" / "fifa24_players.csv",
            # FBRef player statistics
            "fbref_players": self.raw_data_path / "fifa24-25" / "fbref_players.csv",
            # Top 5 leagues statistics
            "top5_leagues": self.raw_data_path / "fifa24-25" / "top5_leagues_stats.csv",
            # Match data
            "matches": self.raw_data_path / "matches" / "matches.csv",
            # Player scores data
            "player_scores": self.raw_data_path / "player_scores" / "players.csv",
        }

        #iterat through each dataset and cheeck if the data os avialable
        for name,path in dataset_paths.items():
            if path.exists():
                try:
                    #low_memory = false will help to read teh datste in chunks
                    self.datasets[name] = pd.read_csv(path, low_memory=False)
                    print(f"✓ Loaded {name}: {self.datasets[name].shape}")
                except Exception as e:
                    print(f"✗ Error loading {name}: {str(e)}")
            else:
                print(f"⚠ File not found: {path}")

    

    #Function for analyzing the missing values
    def analyze_missing_values(self,df:pd.DataFrame,dataset_name:str) -> dict:
        #misiing values per column
        missing_count = df.isnull().sum()
        missing_percentage = (df.isnull().sum() / len(df)) * 100
        #make it a datsframe telling about missing values
        missing_df = pd.DataFrame({
            'missing_count': missing_count,
            'missing_percentage': missing_percentage
        })
        #filtering columns with misisng values
        missing_df = missing_df[missing_df['missing_count']>0]
        missing_df = missing_df.sort_values('missing_count', ascending=False)

        #creating a report for missing values
        report = {
            'total_columns': len(df.columns),
            'columns_with_missing': len(missing_df),
            'columns_without_missing': len(df.columns) - len(missing_df),
            'total_missing_values': int(df.isnull().sum().sum()),
            'missing_details': missing_df.to_dict('index')
        }
        
        return report
    
    #Function for detecting outliers
    def detect_outliers(self,df:pd.DataFrame,datset_name:str) -> dict:
        #selecting numerical columns for outlier detection
        numeric_df = df.select_dtypes(include=[np.number])
        outliers = {}
        for column in numeric_df.columns:
            Q1 = numeric_df[column].quantile(0.25)
            Q3 = numeric_df[column].quantile(0.75)
            IQR = Q3 - Q1
            # Define lower bound for outliers
            lower_bound = Q1 - 1.5 * IQR
            # Define upper bound for outliers
            upper_bound = Q3 + 1.5 * IQR
            # Count values outside the bounds
            outlier_count = ((numeric_df[column] < lower_bound) | 
                           (numeric_df[column] > upper_bound)).sum()
            
            #store the outlier information
            if outlier_count > 0:
                outliers[column] = {
                    'outlier_count': int(outlier_count),
                    'outlier_percentage': float((outlier_count / len(df)) * 100),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound)
                }
        return {
            'total_numeric_columns': len(numeric_df.columns),
            'columns_with_outliers': len(outliers),
            'outlier_details': outliers
        }
    
    #generation of correelation matrix
    def compute_correlation_matrix(self,df:pd.DataFrame,dataset_name:str) -> dict:
        numeric_df = df.select_dtypes(include=[np.number])
        high_correlations = []
        if numeric_df.shape[1] < 2:
            return {'error': 'Insufficient numeric columns for correlation'}
        corr_matrix = numeric_df.corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                # Get correlation value
                corr_value = corr_matrix.iloc[i, j]
                # Check if correlation is strong
                if abs(corr_value) > 0.7:
                    high_correlations.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlations': high_correlations,
            'total_high_correlations': len(high_correlations)
        }
    
    #identifying importat features
    def identify_feature_importance_candidates(self,df:pd.DataFrame,dataset_name:str) -> dict:
        numeric_df = df.select_dtypes(include=[np.number])
        variance = numeric_df.var()
        unique_counts = df.nunique()
        #identifyong igh variance features
        variance_threshold = variance.quantile(0.8)
        high_variance_features = variance[variance > variance_threshold].index.tolist()
        good_cardinality_features = unique_counts[
            (unique_counts > 10) & (unique_counts < len(df) * 0.9)
        ].index.tolist()
        
        return {
            'high_variance_features': high_variance_features,
            'good_cardinality_features': good_cardinality_features,
            'total_numeric_features': len(numeric_df.columns),
            'variance_summary': {
                'mean_variance': float(variance.mean()),
                'median_variance': float(variance.median()),
                'max_variance': float(variance.max()),
                'min_variance': float(variance.min())
            }
        }
    
    #analyzing the match data in datset
    def analyze_match_data(self,df:pd.DataFrame) -> dict:
        match_columns = {
            'goals': ['home_goals', 'away_goals', 'goals', 'home_score', 'away_score'],
            'possession': ['possession', 'home_possession', 'away_possession'],
            'fouls': ['fouls', 'home_fouls', 'away_fouls', 'fouls_committed'],
            'corners': ['corners', 'home_corners', 'away_corners', 'corners_taken'],
            'cards': ['yellow_cards', 'red_cards', 'home_yellow', 'away_yellow', 
                     'home_red', 'away_red'],
            'xg': ['xg', 'home_xg', 'away_xg', 'expected_goals'],
            'betting_odds': ['home_odds', 'draw_odds', 'away_odds', 'odds_home', 
                           'odds_draw', 'odds_away']
        }
        
        analysis = {}

        #analyzing each category
        for category,columns in match_columns.items():
            existing_cols = [col for col in columns if col in df.columns]
            if existing_cols:
                analysis[category] = {
                    'columns_found': existing_cols,
                    'statistics': df[existing_cols].describe().to_dict(),
                    'missing_values': df[existing_cols].isnull().sum().to_dict()
                }
        
        return analysis
    

    #analyzing player daata
    def analyze_player_data(self,df:pd.DataFrame) -> dict:
        player_columns = {
            'age': ['age', 'player_age'],
            'position': ['position', 'player_position', 'role'],
            'rating': ['rating', 'overall', 'player_rating', 'overall_rating'],
            'potential': ['potential', 'player_potential'],
            'market_value': ['market_value', 'value', 'price', 'worth'],
            'wage': ['wage', 'salary', 'weekly_wage']
        }
        analysis={}

        for category, columns in player_columns.items():
            existing_cols = [col for col in columns if col in df.columns]
            if existing_cols:
                numeric_cols = df[existing_cols].select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df[existing_cols].select_dtypes(include=['object', 'category']).columns.tolist()

                analysis[category] = {
                    'columns_found': existing_cols,
                    'numeric_statistics': df[numeric_cols].describe().to_dict() if numeric_cols else {},
                    'categorical_distribution': {},
                    'missing_values': df[existing_cols].isnull().sum().to_dict()
                }

                for col in categorical_cols:
                    analysis[category]['categorical_distribution'][col] = (
                        df[col].value_counts().head(10).to_dict()
                    )
        
        return analysis
    

    #generate data report
    def generate_data_quality_report(self) -> dict:
        quality_report = {
            'timestamp': datetime.now().isoformat(),
            'total_datasets': len(self.datasets),
            'dataset_summaries': {}
        }

        for name, df in self.datasets.items():
            quality_report['dataset_summaries'][name] = {
                'shape': {'rows': int(df.shape[0]), 'columns': int(df.shape[1])},
                'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1024**2),
                'duplicate_rows': int(df.duplicated().sum()),
                'data_types': df.dtypes.astype(str).to_dict(),
                'completeness_score': float((1 - df.isnull().sum().sum() / 
                                           (df.shape[0] * df.shape[1])) * 100)
            }
        
        return quality_report
    
    #running block for eda
    def run_complete_eda(self) -> None:
        print("=" * 60)
        print("StatVault - Exploratory Data Analysis")
        print("=" * 60)

        print("\n[1/6] Loading datasets...")
        self.load_datasets()

        if not self.datasets:
            print("ERROR: No datasets found. Please check data/raw directory.")
            return
        
        all_reports = {
            'timestamp': datetime.now().isoformat(),
            'missing_value_report': {},
            'outlier_report': {},
            'correlation_report': {},
            'feature_importance_candidates': {},
            'match_data_analysis': {},
            'player_data_analysis': {},
            'data_quality_report': {}
        }

        print("\n[2/6] Analyzing missing values...")
        print("[3/6] Detecting outliers...")
        print("[4/6] Computing correlations...")
        print("[5/6] Identifying feature importance candidates...")

        for name, df in self.datasets.items():
            print(f"\n  Processing: {name}")
            # Generate missing value report
            all_reports['missing_value_report'][name] = self.analyze_missing_values(df, name)
            # Generate outlier report
            all_reports['outlier_report'][name] = self.detect_outliers(df, name)
            # Generate correlation report
            all_reports['correlation_report'][name] = self.compute_correlation_matrix(df, name)
            # Generate feature importance candidates
            all_reports['feature_importance_candidates'][name] = (
                self.identify_feature_importance_candidates(df, name)
            )
            # Analyze match-specific data if applicable
            if 'match' in name.lower() or any(col in df.columns for col in 
                ['home_goals', 'away_goals', 'possession', 'home_odds']):
                all_reports['match_data_analysis'][name] = self.analyze_match_data(df)
            # Analyze player-specific data if applicable
            if 'player' in name.lower() or 'fifa' in name.lower():
                all_reports['player_data_analysis'][name] = self.analyze_player_data(df)
        # Step 3: Generate overall data quality report
        print("\n[6/6] Generating data quality report...")
        all_reports['data_quality_report'] = self.generate_data_quality_report()
        # Step 4: Save all reports to disk
        print("\nSaving reports...")
        # Save complete report as JSON
        report_path = self.reports_path / "eda_complete_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(all_reports, f, indent=2, default=str)
        print(f"✓ Saved: {report_path}")
        
        # Save individual reports for easier access
        # Missing value report
        missing_path = self.reports_path / "missing_values_report.json"
        with open(missing_path, 'w', encoding='utf-8') as f:
            json.dump(all_reports['missing_value_report'], f, indent=2, default=str)
        print(f"✓ Saved: {missing_path}")
        # Outlier report
        outlier_path = self.reports_path / "outlier_report.json"
        with open(outlier_path, 'w', encoding='utf-8') as f:
            json.dump(all_reports['outlier_report'], f, indent=2, default=str)
        print(f"✓ Saved: {outlier_path}")
        # Correlation report
        correlation_path = self.reports_path / "correlation_report.json"
        with open(correlation_path, 'w', encoding='utf-8') as f:
            json.dump(all_reports['correlation_report'], f, indent=2, default=str)
        print(f"✓ Saved: {correlation_path}")
        # Feature importance candidates
        feature_path = self.reports_path / "feature_analysis_report.json"
        with open(feature_path, 'w', encoding='utf-8') as f:
            json.dump(all_reports['feature_importance_candidates'], f, indent=2, default=str)
        print(f"✓ Saved: {feature_path}")
        # Data quality report
        quality_path = self.reports_path / "data_quality_report.json"
        with open(quality_path, 'w', encoding='utf-8') as f:
            json.dump(all_reports['data_quality_report'], f, indent=2, default=str)
        print(f"✓ Saved: {quality_path}")
        
        # Step 5: Print summary
        print("\n" + "=" * 60)
        print("EDA COMPLETE - Summary")
        print("=" * 60)
        print(f"Datasets analyzed: {len(self.datasets)}")
        print(f"Reports generated: 5")
        print(f"Output directory: {self.reports_path.absolute()}")
        print("=" * 60)
        # Store reports for programmatic access
        self.reports = all_reports


#function block to run the whole code

def main():
    if '__file__' in dir():
        project_root = Path(__file__).resolve().parent.parent
    else:
        project_root = Path.cwd().parent
    analyzer = DataQualityAnalyzer(base_path=str(project_root))
    analyzer.run_complete_eda()
    print(f"Project Root: {project_root}")
    print(f"Raw Data Path: {analyzer.raw_data_path}")
    print(f"Reports Path: {analyzer.reports_path}")
    
    return analyzer

if __name__ == "__main__":
    analyzer = main()

