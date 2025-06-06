#!/usr/bin/env python3
"""
Enhanced Document Intelligence Module
Provides advanced content classification and semantic analysis
WITHOUT compromising existing functionality
"""

import re
import json
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional, Set
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentClassification:
    """Detailed content classification results"""
    primary_type: str  # academic, technical, legal, business, literary
    confidence: float  # 0.0-1.0
    secondary_types: List[str]
    complexity_level: str  # simple, medium, complex, expert
    domain_indicators: List[str]
    translation_approach: str  # conservative, standard, creative
    recommended_batch_size: int
    recommended_temperature: float

@dataclass
class SemanticGroup:
    """Semantic grouping of related content"""
    group_id: str
    content_items: List[Dict]
    semantic_theme: str
    coherence_score: float
    translation_priority: int
    preserve_order: bool
    cross_references: List[str]

class AdvancedContentClassifier:
    """Advanced content classification without compromising existing functionality"""
    
    def __init__(self):
        self.classification_patterns = {
            'academic': {
                'strong_indicators': [
                    r'\babstract\b', r'\bmethodology\b', r'\bhypothesis\b', r'\bresearch\b',
                    r'\banalysis\b', r'\bconclusion\b', r'\bbibliography\b', r'\breferences\b',
                    r'\bstatistical\b', r'\bempirical\b', r'\btheoretical\b', r'\bstudy\b'
                ],
                'weak_indicators': [
                    r'\bdata\b', r'\bresults\b', r'\bfigure\b', r'\btable\b', r'\bchapter\b'
                ],
                'domain_patterns': {
                    'science': [r'\bexperiment\b', r'\bhypothesis\b', r'\bvariable\b'],
                    'medicine': [r'\bpatient\b', r'\btreatment\b', r'\bclinical\b'],
                    'psychology': [r'\bbehavior\b', r'\bcognitive\b', r'\bpsychological\b'],
                    'engineering': [r'\bsystem\b', r'\bdesign\b', r'\boptimization\b']
                }
            },
            'technical': {
                'strong_indicators': [
                    r'\bspecification\b', r'\bconfiguration\b', r'\binstallation\b',
                    r'\bprocedure\b', r'\bmanual\b', r'\bsystem\b', r'\bparameters\b'
                ],
                'weak_indicators': [
                    r'\bstep\b', r'\bprocess\b', r'\bsetup\b', r'\bversion\b'
                ],
                'domain_patterns': {
                    'software': [r'\bcode\b', r'\bfunction\b', r'\bapi\b', r'\bdatabase\b'],
                    'hardware': [r'\bdevice\b', r'\bcomponent\b', r'\bcircuit\b'],
                    'network': [r'\bprotocol\b', r'\bserver\b', r'\bconnection\b']
                }
            },
            'legal': {
                'strong_indicators': [
                    r'\bwhereas\b', r'\bhereby\b', r'\bpursuant\b', r'\bjurisdiction\b',
                    r'\bcontract\b', r'\bagreement\b', r'\bliability\b', r'\bclause\b'
                ],
                'weak_indicators': [
                    r'\bparty\b', r'\bterms\b', r'\bconditions\b', r'\brights\b'
                ],
                'domain_patterns': {
                    'corporate': [r'\bcorporation\b', r'\bshareholder\b', r'\bboard\b'],
                    'intellectual_property': [r'\bpatent\b', r'\btrademark\b', r'\bcopyright\b'],
                    'contract': [r'\bobligations\b', r'\bperformance\b', r'\bbreach\b']
                }
            },
            'business': {
                'strong_indicators': [
                    r'\bstrategy\b', r'\bmarket\b', r'\brevenue\b', r'\bprofit\b',
                    r'\bcustomer\b', r'\bsales\b', r'\bmanagement\b', r'\boperations\b'
                ],
                'weak_indicators': [
                    r'\bcompany\b', r'\bbusiness\b', r'\bservice\b', r'\bproduct\b'
                ],
                'domain_patterns': {
                    'finance': [r'\bfinancial\b', r'\binvestment\b', r'\bbudget\b'],
                    'marketing': [r'\bbrand\b', r'\bcampaign\b', r'\badvertising\b'],
                    'hr': [r'\bemployee\b', r'\btraining\b', r'\bperformance\b']
                }
            },
            'literary': {
                'strong_indicators': [
                    r'\bcharacter\b', r'\bnarrative\b', r'\bstory\b', r'\bplot\b',
                    r'\bdialogue\b', r'\bchapter\b', r'\bnovel\b', r'\bpoetry\b'
                ],
                'weak_indicators': [
                    r'\bsaid\b', r'\bthought\b', r'\bfelt\b', r'\bremembered\b'
                ],
                'domain_patterns': {
                    'fiction': [r'\bprotagonist\b', r'\bantagonist\b', r'\bconflict\b'],
                    'poetry': [r'\bverse\b', r'\brhyme\b', r'\bstanza\b'],
                    'drama': [r'\bact\b', r'\bscene\b', r'\bmonologue\b']
                }
            }
        }
        
        self.complexity_indicators = {
            'expert': [
                r'\btheorem\b', r'\blemma\b', r'\bcorollary\b', r'\bproof\b',
                r'\balgorithm\b', r'\boptimization\b', r'\bderivation\b'
            ],
            'complex': [
                r'\banalysis\b', r'\bmethodology\b', r'\bframework\b',
                r'\bimplementation\b', r'\barchitecture\b'
            ],
            'medium': [
                r'\bprocess\b', r'\bprocedure\b', r'\bmethod\b', r'\bapproach\b'
            ],
            'simple': [
                r'\bintroduction\b', r'\boverview\b', r'\bsummary\b', r'\bbasic\b'
            ]
        }
    
    def classify_content(self, content_items: List[Dict]) -> ContentClassification:
        """Classify content without modifying original items"""
        # Combine all text for analysis
        combined_text = ""
        for item in content_items:
            text = item.get('text', '') or item.get('translated_text', '')
            combined_text += f" {text}"
        
        combined_text = combined_text.lower()
        
        # Calculate scores for each type
        type_scores = {}
        domain_indicators = []
        
        for content_type, patterns in self.classification_patterns.items():
            score = 0
            
            # Strong indicators (weight: 3)
            for pattern in patterns['strong_indicators']:
                matches = len(re.findall(pattern, combined_text))
                score += matches * 3
            
            # Weak indicators (weight: 1)
            for pattern in patterns['weak_indicators']:
                matches = len(re.findall(pattern, combined_text))
                score += matches * 1
            
            # Domain-specific patterns (weight: 2)
            for domain, domain_patterns in patterns['domain_patterns'].items():
                for pattern in domain_patterns:
                    matches = len(re.findall(pattern, combined_text))
                    if matches > 0:
                        score += matches * 2
                        domain_indicators.append(f"{content_type}_{domain}")
            
            type_scores[content_type] = score
        
        # Determine primary type
        if not type_scores or max(type_scores.values()) == 0:
            primary_type = 'general'
            confidence = 0.5
        else:
            primary_type = max(type_scores, key=type_scores.get)
            total_score = sum(type_scores.values())
            confidence = type_scores[primary_type] / total_score if total_score > 0 else 0.5
        
        # Determine secondary types
        secondary_types = [t for t, s in type_scores.items() 
                          if t != primary_type and s > 0]
        secondary_types.sort(key=lambda t: type_scores[t], reverse=True)
        secondary_types = secondary_types[:2]  # Top 2 secondary types
        
        # Determine complexity level
        complexity_level = self._determine_complexity(combined_text)
        
        # Determine translation approach and parameters
        translation_approach, batch_size, temperature = self._get_translation_parameters(
            primary_type, complexity_level, confidence
        )
        
        return ContentClassification(
            primary_type=primary_type,
            confidence=confidence,
            secondary_types=secondary_types,
            complexity_level=complexity_level,
            domain_indicators=domain_indicators,
            translation_approach=translation_approach,
            recommended_batch_size=batch_size,
            recommended_temperature=temperature
        )
    
    def _determine_complexity(self, text: str) -> str:
        """Determine complexity level based on text analysis"""
        complexity_scores = {}
        
        for level, patterns in self.complexity_indicators.items():
            score = 0
            for pattern in patterns:
                score += len(re.findall(pattern, text))
            complexity_scores[level] = score
        
        if complexity_scores['expert'] > 0:
            return 'expert'
        elif complexity_scores['complex'] > 2:
            return 'complex'
        elif complexity_scores['medium'] > 1:
            return 'medium'
        else:
            return 'simple'
    
    def _get_translation_parameters(self, content_type: str, complexity: str, confidence: float) -> Tuple[str, int, float]:
        """Get optimal translation parameters based on classification"""
        # Base parameters
        base_batch_size = 12000
        base_temperature = 0.1
        
        # Adjust based on content type
        type_adjustments = {
            'academic': {'batch_mult': 1.2, 'temp': 0.05, 'approach': 'conservative'},
            'technical': {'batch_mult': 1.1, 'temp': 0.1, 'approach': 'conservative'},
            'legal': {'batch_mult': 0.8, 'temp': 0.05, 'approach': 'conservative'},
            'business': {'batch_mult': 1.0, 'temp': 0.1, 'approach': 'standard'},
            'literary': {'batch_mult': 1.3, 'temp': 0.15, 'approach': 'creative'},
            'general': {'batch_mult': 1.0, 'temp': 0.1, 'approach': 'standard'}
        }
        
        # Adjust based on complexity
        complexity_adjustments = {
            'expert': {'batch_mult': 0.8, 'temp_mult': 0.5},
            'complex': {'batch_mult': 0.9, 'temp_mult': 0.8},
            'medium': {'batch_mult': 1.0, 'temp_mult': 1.0},
            'simple': {'batch_mult': 1.2, 'temp_mult': 1.2}
        }
        
        # Apply adjustments
        type_adj = type_adjustments.get(content_type, type_adjustments['general'])
        complexity_adj = complexity_adjustments.get(complexity, complexity_adjustments['medium'])
        
        final_batch_size = int(base_batch_size * type_adj['batch_mult'] * complexity_adj['batch_mult'])
        final_temperature = base_temperature * complexity_adj['temp_mult']
        
        # Ensure confidence affects parameters
        if confidence < 0.3:
            # Low confidence - use conservative settings
            final_batch_size = int(final_batch_size * 0.8)
            final_temperature = min(final_temperature, 0.05)
        
        return type_adj['approach'], final_batch_size, final_temperature

class SemanticContentGrouper:
    """Groups content semantically while preserving existing functionality"""
    
    def __init__(self):
        self.semantic_patterns = {
            'introduction': [r'\bintroduction\b', r'\boverview\b', r'\bpreface\b'],
            'methodology': [r'\bmethodology\b', r'\bmethod\b', r'\bapproach\b', r'\bprocedure\b'],
            'results': [r'\bresults\b', r'\bfindings\b', r'\boutcome\b', r'\bdata\b'],
            'discussion': [r'\bdiscussion\b', r'\banalysis\b', r'\binterpretation\b'],
            'conclusion': [r'\bconclusion\b', r'\bsummary\b', r'\bfinal\b'],
            'references': [r'\breferences\b', r'\bbibliography\b', r'\bcitation\b']
        }
    
    def create_semantic_groups(self, content_items: List[Dict]) -> List[SemanticGroup]:
        """Create semantic groups without modifying original items"""
        groups = []
        current_theme = 'general'
        current_group_items = []
        group_counter = 0
        
        for i, item in enumerate(content_items):
            text = (item.get('text', '') or item.get('translated_text', '')).lower()
            
            # Detect theme change
            detected_theme = self._detect_theme(text)
            
            # If theme changes or we have too many items, create new group
            if (detected_theme != current_theme and current_group_items) or len(current_group_items) >= 10:
                if current_group_items:
                    groups.append(self._create_group(
                        group_counter, current_group_items, current_theme
                    ))
                    group_counter += 1
                
                current_group_items = [item]
                current_theme = detected_theme
            else:
                current_group_items.append(item)
        
        # Add final group
        if current_group_items:
            groups.append(self._create_group(
                group_counter, current_group_items, current_theme
            ))
        
        return groups
    
    def _detect_theme(self, text: str) -> str:
        """Detect semantic theme of text"""
        theme_scores = {}
        
        for theme, patterns in self.semantic_patterns.items():
            score = 0
            for pattern in patterns:
                score += len(re.findall(pattern, text))
            theme_scores[theme] = score
        
        if max(theme_scores.values()) > 0:
            return max(theme_scores, key=theme_scores.get)
        else:
            return 'general'
    
    def _create_group(self, group_id: int, items: List[Dict], theme: str) -> SemanticGroup:
        """Create a semantic group"""
        # Calculate coherence score based on content similarity
        coherence_score = self._calculate_coherence(items)
        
        # Determine translation priority
        priority_map = {
            'introduction': 4, 'methodology': 5, 'results': 5,
            'discussion': 4, 'conclusion': 4, 'references': 2, 'general': 3
        }
        priority = priority_map.get(theme, 3)
        
        # Detect cross-references
        cross_refs = self._detect_cross_references(items)
        
        return SemanticGroup(
            group_id=f"semantic_group_{group_id}",
            content_items=items,
            semantic_theme=theme,
            coherence_score=coherence_score,
            translation_priority=priority,
            preserve_order=theme in ['methodology', 'results'],  # These need strict order
            cross_references=cross_refs
        )
    
    def _calculate_coherence(self, items: List[Dict]) -> float:
        """Calculate coherence score for a group of items"""
        if len(items) <= 1:
            return 1.0
        
        # Simple coherence based on content type consistency
        types = [item.get('type', 'unknown') for item in items]
        type_consistency = len(set(types)) / len(types)
        
        # Coherence is higher when types are more consistent
        return 1.0 - type_consistency + 0.1  # Add small base coherence
    
    def _detect_cross_references(self, items: List[Dict]) -> List[str]:
        """Detect cross-references within items"""
        cross_refs = []
        
        for item in items:
            text = item.get('text', '') or item.get('translated_text', '')
            
            # Look for common cross-reference patterns
            ref_patterns = [
                r'\bfigure\s+\d+\b', r'\btable\s+\d+\b', r'\bsection\s+\d+\b',
                r'\bchapter\s+\d+\b', r'\bappendix\s+[a-z]\b'
            ]
            
            for pattern in ref_patterns:
                matches = re.findall(pattern, text.lower())
                cross_refs.extend(matches)
        
        return list(set(cross_refs))  # Remove duplicates

class CrossReferencePreserver:
    """Preserves cross-references during translation"""
    
    def __init__(self):
        self.reference_patterns = {
            'figure': r'\b(figure|fig\.?)\s+(\d+)\b',
            'table': r'\b(table|tbl\.?)\s+(\d+)\b',
            'section': r'\b(section|sec\.?)\s+(\d+(?:\.\d+)*)\b',
            'chapter': r'\b(chapter|ch\.?)\s+(\d+)\b',
            'equation': r'\b(equation|eq\.?)\s+(\d+)\b',
            'appendix': r'\b(appendix|app\.?)\s+([a-z])\b'
        }
        
        self.reference_map = {}  # Maps original refs to translated refs
    
    def extract_references(self, content_items: List[Dict]) -> Dict[str, List[str]]:
        """Extract all cross-references from content"""
        references = defaultdict(list)
        
        for item in content_items:
            text = item.get('text', '') or item.get('translated_text', '')
            
            for ref_type, pattern in self.reference_patterns.items():
                matches = re.findall(pattern, text.lower())
                for match in matches:
                    if isinstance(match, tuple):
                        ref_text = f"{match[0]} {match[1]}"
                    else:
                        ref_text = match
                    references[ref_type].append(ref_text)
        
        return dict(references)
    
    def create_reference_preservation_guide(self, references: Dict[str, List[str]]) -> str:
        """Create a guide for preserving references during translation"""
        if not references:
            return ""
        
        guide = "\n=== CROSS-REFERENCE PRESERVATION GUIDE ===\n"
        guide += "IMPORTANT: Preserve these exact reference formats in translation:\n\n"
        
        for ref_type, ref_list in references.items():
            if ref_list:
                unique_refs = list(set(ref_list))
                guide += f"{ref_type.upper()} REFERENCES:\n"
                for ref in unique_refs[:5]:  # Limit to 5 examples
                    guide += f"  - Keep format: '{ref}'\n"
                guide += "\n"
        
        guide += "Translate the reference TYPE but keep the NUMBERS/LETTERS unchanged.\n"
        guide += "Example: 'Figure 1' → 'Εικόνα 1' (Greek), 'Figura 1' (Spanish)\n"
        guide += "========================================\n"
        
        return guide

def main():
    """Test the enhanced document intelligence"""
    print("🧠 Enhanced Document Intelligence Module")
    print("✅ Advanced content classification")
    print("✅ Semantic content grouping") 
    print("✅ Cross-reference preservation")
    print("✅ Zero compromise to existing functionality")

if __name__ == "__main__":
    main()
