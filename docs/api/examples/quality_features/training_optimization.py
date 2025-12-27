"""
Training Data Optimization Example

This example demonstrates how to optimize training data for
better voice cloning quality (IDEA 68).
"""

import requests

BASE_URL = "http://localhost:8000/api"


def optimize_training_data(dataset_id, analyze_quality=True, select_optimal=True):
    """
    Optimize training dataset by analyzing quality and selecting optimal samples.
    
    Args:
        dataset_id: Dataset ID to optimize
        analyze_quality: Analyze data quality (default: True)
        select_optimal: Select optimal samples (default: True)
    
    Returns:
        TrainingDataOptimizationResponse with analysis and optimized dataset
    """
    url = f"{BASE_URL}/training/datasets/{dataset_id}/optimize"
    
    data = {
        "dataset_id": dataset_id,
        "analyze_quality": analyze_quality,
        "select_optimal": select_optimal,
        "suggest_augmentation": True,
        "analyze_diversity": True
    }
    
    print(f"Optimizing training dataset: {dataset_id}...")
    response = requests.post(url, json=data)
    response.raise_for_status()
    
    result = response.json()
    
    print(f"\n✅ Training data optimization complete!")
    
    # Show analysis
    analysis = result['analysis']
    print(f"\nAnalysis Results:")
    print(f"  Quality score: {analysis['quality_score']:.1f}/10.0")
    print(f"  Diversity score: {analysis['diversity_score']:.1f}/10.0")
    print(f"  Coverage score: {analysis['coverage_score']:.1f}/10.0")
    
    # Show optimal samples
    if analysis.get('optimal_samples'):
        print(f"\nOptimal Samples Selected: {len(analysis['optimal_samples'])}")
        for sample in analysis['optimal_samples'][:5]:  # Show first 5
            print(f"  - {sample}")
        if len(analysis['optimal_samples']) > 5:
            print(f"  ... and {len(analysis['optimal_samples']) - 5} more")
    
    # Show recommendations
    if analysis.get('recommendations'):
        print(f"\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  - {rec}")
    
    # Show augmentation suggestions
    if analysis.get('augmentation_suggestions'):
        print(f"\nAugmentation Suggestions:")
        for suggestion in analysis['augmentation_suggestions']:
            print(f"  - {suggestion}")
    
    # Show optimized dataset if created
    if result.get('optimized_dataset_id'):
        print(f"\n✅ Optimized dataset created!")
        print(f"  Optimized dataset ID: {result['optimized_dataset_id']}")
        print(f"  Quality improvement: {result['quality_improvement']:.2%}")
    
    return result


def optimize_training_data_workflow(dataset_id):
    """
    Complete workflow for training data optimization.
    """
    # Step 1: Analyze current dataset
    print("=== Step 1: Analyze Training Data ===")
    result = optimize_training_data(
        dataset_id=dataset_id,
        analyze_quality=True,
        select_optimal=True
    )
    
    # Step 2: Use optimized dataset if quality improved
    if result.get('optimized_dataset_id') and result['quality_improvement'] > 0.1:
        print(f"\n=== Step 2: Use Optimized Dataset ===")
        print(f"Use optimized dataset ID: {result['optimized_dataset_id']}")
        print("Quality improvement significant - recommended to use optimized dataset")
    
    return result


if __name__ == "__main__":
    # Example usage
    dataset_id = "dataset-123"
    
    result = optimize_training_data(
        dataset_id=dataset_id,
        analyze_quality=True,
        select_optimal=True
    )
    
    if result.get('optimized_dataset_id'):
        print(f"\nUse optimized dataset: {result['optimized_dataset_id']}")

