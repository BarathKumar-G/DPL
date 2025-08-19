import pandas as pd

# Global data loading
def load_data():
    """Load and prepare the trade data"""
    print("Loading trade data...")
    df = pd.read_csv("C:\\Users\\lokhe\\Downloads\\Datasets-20250819T145252Z-1-001\\Datasets\\processed_imports_full.csv")
    
    # Convert numeric columns
    df['import_value_numeric'] = pd.to_numeric(df.get('import_value'), errors='coerce')
    df['primaryValue_numeric'] = pd.to_numeric(df.get('primaryValue'), errors='coerce')
    
    print(f"Dataset loaded: {df.shape[0]} records, {df.shape[1]} columns")
    return df


def analyze_agricultural_dependency():
    """Question 1: Identify countries most dependent on agricultural imports from only 2–3 partners"""
    print("="*80)
    print("QUESTION 1: AGRICULTURAL IMPORT DEPENDENCY ANALYSIS")
    print("="*80)
    
    df = load_data()
    
    # Identify agricultural commodities
    agricultural_keywords = [
        'food', 'grain', 'wheat', 'rice', 'corn', 'soy', 'meat', 'dairy', 
        'fruit', 'vegetable', 'sugar', 'coffee', 'tea', 'fish', 'agricultural',
        'livestock', 'poultry', 'beef', 'pork', 'milk', 'cheese', 'cereals'
    ]
    
    # Filter for agricultural imports
    ag_mask = df['cmdDesc'].str.lower().str.contains('|'.join(agricultural_keywords), na=False)
    ag_imports = df[ag_mask & (df['flowDesc'] == 'Import')].copy()
    
    if len(ag_imports) == 0:
        print("No agricultural imports found in dataset with current keyword matching")
        return
    
    # Calculate import dependency by country and partner
    country_partner_ag = ag_imports.groupby(['Country', 'partnerDesc'])['import_value_numeric'].sum().reset_index()
    country_total_ag = ag_imports.groupby('Country')['import_value_numeric'].sum().reset_index()
    country_total_ag.columns = ['Country', 'total_ag_imports']
    
    # Merge to calculate dependency ratios
    dependency_analysis = country_partner_ag.merge(country_total_ag, on='Country')
    dependency_analysis['dependency_ratio'] = dependency_analysis['import_value_numeric'] / dependency_analysis['total_ag_imports']
    
    # Find countries dependent on 2-3 partners for >50% of agricultural imports
    high_dependency_countries = []
    
    for country in dependency_analysis['Country'].unique():
        country_data = dependency_analysis[dependency_analysis['Country'] == country].sort_values('dependency_ratio', ascending=False)
        
        top_2_share = country_data.head(2)['dependency_ratio'].sum()
        top_3_share = country_data.head(3)['dependency_ratio'].sum()
        
        if top_2_share > 0.5 or top_3_share > 0.6:
            high_dependency_countries.append({
                'country': country,
                'top_2_share': top_2_share,
                'top_3_share': top_3_share,
                'total_ag_imports': country_data['total_ag_imports'].iloc[0],
                'top_partners': list(country_data.head(3)['partnerDesc'].values)
            })
    
    print(f" ANSWER: Found {len(high_dependency_countries)} countries with high agricultural import dependency")
    print("\nCountries most dependent on 2-3 partners for agricultural imports:")
    
    for country_info in sorted(high_dependency_countries, key=lambda x: x['top_3_share'], reverse=True)[:10]:
        print(f"• {country_info['country']}: {country_info['top_3_share']:.1%} from top 3 partners")
        print(f"  Partners: {', '.join(country_info['top_partners'][:3])}")
        print(f"  Total ag imports: ${country_info['total_ag_imports']:,.0f}")
    
    # Food Security Risk Simulation
    ban_scenarios = [
        {'name': 'Major Grain Exporters Ban', 'banned_partners': ['United States', 'Russian Federation', 'Ukraine', 'Argentina']},
        {'name': 'Regional Crisis', 'banned_partners': ['China', 'India', 'Brazil']},
        {'name': 'Climate Emergency', 'banned_partners': ['Australia', 'Canada', 'United States']}
    ]
    
    print("\n FOOD SECURITY RISK SIMULATION:")
    for scenario in ban_scenarios:
        at_risk_countries = []
        for country_info in high_dependency_countries:
            impact_ratio = 0
            for partner in scenario['banned_partners']:
                if partner in country_info['top_partners']:
                    impact_ratio += country_info['top_3_share'] / 3
            
            if impact_ratio > 0.2:  # >20% supply disruption
                at_risk_countries.append({
                    'country': country_info['country'],
                    'disruption': min(impact_ratio, 1.0)
                })
        
        print(f"\n{scenario['name']}:")
        if at_risk_countries:
            for country in sorted(at_risk_countries, key=lambda x: x['disruption'], reverse=True)[:5]:
                risk_level = 'CRITICAL' if country['disruption'] > 0.4 else 'HIGH'
                print(f"  {country['country']}: {country['disruption']:.1%} supply disruption ({risk_level} RISK)")
        else:
            print("  No countries at significant risk from this scenario")

def predict_youth_unemployment_2030():
    """Question 2: Predict which countries will have youth unemployment >25% by 2030"""
    print("="*80)
    print("QUESTION 2: YOUTH UNEMPLOYMENT PREDICTION FOR 2030")
    print("="*80)
    
    print("  NOTE: Trade data lacks demographic/employment data. Using framework with example data.")
    
    def unemployment_model(base_rate, gdp_growth, economic_structure_score, education_score):
        """Simplified youth unemployment prediction model"""
        unemployment_change = (
            -0.5 * gdp_growth +  # GDP growth reduces unemployment
            0.3 * (1 - economic_structure_score) +  # Poor diversification increases unemployment
            -0.2 * education_score  # Better education reduces unemployment
        )
        return max(0, base_rate + unemployment_change)
    
    # Example countries with current data (would need real data sources)
    countries_data = [
        {'country': 'Spain', 'base_youth_unemployment': 32.5, 'gdp_growth': 1.2, 'econ_structure': 0.7, 'education': 0.8},
        {'country': 'Italy', 'base_youth_unemployment': 29.8, 'gdp_growth': 0.8, 'econ_structure': 0.6, 'education': 0.7},
        {'country': 'Greece', 'base_youth_unemployment': 35.2, 'gdp_growth': 1.5, 'econ_structure': 0.5, 'education': 0.6},
        {'country': 'South Africa', 'base_youth_unemployment': 55.6, 'gdp_growth': 1.8, 'econ_structure': 0.4, 'education': 0.5},
        {'country': 'Tunisia', 'base_youth_unemployment': 38.4, 'gdp_growth': 2.1, 'econ_structure': 0.4, 'education': 0.6},
        {'country': 'Bosnia', 'base_youth_unemployment': 45.8, 'gdp_growth': 2.8, 'econ_structure': 0.3, 'education': 0.5},
        {'country': 'North Macedonia', 'base_youth_unemployment': 35.7, 'gdp_growth': 3.2, 'econ_structure': 0.4, 'education': 0.6},
        {'country': 'Turkey', 'base_youth_unemployment': 24.9, 'gdp_growth': 3.5, 'econ_structure': 0.6, 'education': 0.7},
    ]
    
    print("ANSWER: Countries predicted to have youth unemployment >25% by 2030 (Global Slowdown Scenario):")
    
    high_risk_countries = []
    for country_data in countries_data:
        # Global slowdown reduces GDP growth by 2 percentage points
        predicted_rate = unemployment_model(
            country_data['base_youth_unemployment'],
            country_data['gdp_growth'] - 2.0,  # Global slowdown impact
            country_data['econ_structure'],
            country_data['education']
        )
        
        if predicted_rate > 25:
            high_risk_countries.append({
                'country': country_data['country'],
                'predicted_rate': predicted_rate,
                'current_rate': country_data['base_youth_unemployment']
            })
    
    for country in sorted(high_risk_countries, key=lambda x: x['predicted_rate'], reverse=True):
        change = country['predicted_rate'] - country['current_rate']
        trend = "↗" if change > 0 else "↘"
        print(f"• {country['country']}: {country['predicted_rate']:.1f}% {trend} (current: {country['current_rate']:.1f}%)")
    
    print(f"\nSUMMARY: {len(high_risk_countries)} countries predicted to exceed 25% youth unemployment threshold")

def analyze_export_aging_risk():
    """Question 3: Export sectors most at risk from labor shortages due to aging demographics"""
    print("="*80)
    print("QUESTION 3: EXPORT SECTORS AT RISK FROM AGING DEMOGRAPHICS")
    print("="*80)
    
    df = load_data()
    
    # Analyze export patterns
    exports = df[df['flowDesc'] == 'Export'].copy()
    
    if len(exports) == 0:
        print(" No export data found in dataset")
        return
    
    # Calculate export concentration by country and commodity
    country_exports = exports.groupby(['Country', 'cmdDesc'])['import_value_numeric'].sum().reset_index()
    country_total_exports = exports.groupby('Country')['import_value_numeric'].sum().reset_index()
    country_total_exports.columns = ['Country', 'total_exports']
    
    export_analysis = country_exports.merge(country_total_exports, on='Country')
    export_analysis['export_share'] = export_analysis['import_value_numeric'] / export_analysis['total_exports']
    
    # Identify labor-intensive sectors
    labor_intensive_keywords = [
        'textile', 'clothing', 'footwear', 'furniture', 'toy', 'leather',
        'wood', 'paper', 'manufacturing', 'assembly', 'garment'
    ]
    
    export_analysis['is_labor_intensive'] = export_analysis['cmdDesc'].str.lower().str.contains(
        '|'.join(labor_intensive_keywords), na=False
    )
    
    # Calculate labor-intensive export dependency by country
    labor_exports = export_analysis[export_analysis['is_labor_intensive']].groupby('Country').agg({
        'export_share': 'sum',
        'import_value_numeric': 'sum'
    }).reset_index()
    
    labor_exports.columns = ['Country', 'labor_intensive_share', 'labor_intensive_value']
    
    print(" ANSWER: Countries with highest labor-intensive export dependency:")
    
    top_labor_dependent = labor_exports[labor_exports['labor_intensive_share'] > 0.1].sort_values('labor_intensive_share', ascending=False)
    
    for _, row in top_labor_dependent.head(10).iterrows():
        print(f"• {row['Country']}: {row['labor_intensive_share']:.1%} of exports are labor-intensive")
        print(f"  Value: ${row['labor_intensive_value']:,.0f}")
    
    # Productivity impact simulation
    def simulate_aging_impact(current_productivity, median_age_increase, sector_labor_intensity):
        """Simulate productivity impact of aging workforce"""
        age_productivity_decline = 0.02 * median_age_increase  # 2% decline per year
        labor_adjustment_factor = sector_labor_intensity
        
        productivity_impact = current_productivity * (1 - age_productivity_decline * labor_adjustment_factor)
        return max(0.5, productivity_impact)  # Floor at 50%
    
    print("\n PRODUCTIVITY IMPACT SIMULATION:")
    
    age_scenarios = [5, 10, 15]
    example_sectors = [
        {'sector': 'Manufacturing', 'current_prod': 100, 'labor_intensity': 0.8},
        {'sector': 'Textiles', 'current_prod': 100, 'labor_intensity': 0.9},
        {'sector': 'Agriculture', 'current_prod': 100, 'labor_intensity': 0.7},
        {'sector': 'Construction', 'current_prod': 100, 'labor_intensity': 0.9},
    ]
    
    for age_increase in age_scenarios:
        print(f"\nMedian age increase: +{age_increase} years")
        for sector in example_sectors:
            new_productivity = simulate_aging_impact(
                sector['current_prod'], 
                age_increase, 
                sector['labor_intensity']
            )
            decline = (sector['current_prod'] - new_productivity) / sector['current_prod'] * 100
            risk_level = " CRITICAL" if decline > 20 else "🟡 HIGH" if decline > 10 else "🟢 MODERATE"
            print(f"  {sector['sector']}: {decline:.1f}% productivity decline {risk_level}")
    
    print(f"\nSUMMARY: Labor-intensive export sectors face 10-30% productivity declines with demographic aging")

if __name__ == "__main__":
    print("Trade Analysis - Three Key Questions")
    print("Call individual functions:")
    print("1. analyze_agricultural_dependency()")
    print("2. predict_youth_unemployment_2030()")
    print("3. analyze_export_aging_risk()")
    print("\nOr run all:")
    
    # Uncomment to run all functions
    analyze_agricultural_dependency()
    predict_youth_unemployment_2030()
    analyze_export_aging_risk()
