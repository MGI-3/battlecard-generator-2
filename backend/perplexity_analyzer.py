# import requests
# import json
# from typing import List, Dict, Optional
# import re

# class PerplexityAnalyzer:
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         self.base_url = "https://api.perplexity.ai/chat/completions"
#         self.headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         }

#     def analyze_text(self, text: str) -> List[Dict]:
#         """
#         Analyze text using Perplexity AI to generate battlecards.
#         """
#         # # Truncate text if it's too long
#         # max_text_length = 15000
#         # if len(text) > max_text_length:
#         #     text = text[:max_text_length]
        
#         # First, extract potential case studies from the text
#         case_studies = self._extract_potential_case_studies(text)
#         case_studies_str = "\n\n".join(case_studies) if case_studies else "No explicit case studies found."
        
#         prompt = f"""
#         Analyze the following text and generate comprehensive battlecards. 
#         Each battlecard should contain:
#         1. A specific problem area or need that the company/product addresses
#         2. A detailed problem description (up to 100 words) that explains the challenge faced by clients
#         3. Solutions and differentiators (up to 100 words) that highlight unique value propositions
#         4. Case studies that demonstrate the solution in real-world scenarios

#         Pay special attention to these POTENTIAL CASE STUDIES found in the text:
#         {case_studies_str}

#         Format the response as a JSON array of battlecards with these exact keys:
#         [
#             {{
#                 "problem_area": "Problem area title",
#                 "problem_description": "Thorough explanation of the problem",
#                 "differentiator": "Detailed solution and unique value proposition",
#                 "case_studies": ["Case study 1", "Case study 2"]
#             }}
#         ]

#         IMPORTANT GUIDELINES:
#         - Each battlecard should focus on a different problem area or need
#         - The problem description should directly relate to the case studies but do not include the text of case studies
#         - Make differentiators specific and substantive, avoiding vague marketing language
#         - Don't include comments about word count in your response
#         - Ensure case studies include specific results, clients, or implementations whenever possible
#         - Focus on quality so that there will not be any hallucinations

#         Text to analyze:
#         {text}
#         """

#         try:
#             payload = {
#                 "model": "sonar-reasoning",
#                 "messages": [{"role": "user", "content": prompt}],
#                 "temperature": 0.7,
#                 "max_tokens": 3000
#             }
            
#             print("Sending request to Perplexity API...")
#             print(f"Using model: {payload['model']}")
            
#             response = requests.post(
#                 self.base_url,
#                 headers=self.headers,
#                 json=payload
#             )
            
#             if response.status_code != 200:
#                 print(f"API Error: {response.status_code} - {response.text}")
#                 raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
#             result = response.json()
            
#             # Extract and parse the battlecards from the response
#             content = result["choices"][0]["message"]["content"]
#             battlecards = self._parse_response(content)
            
#             # If no case studies were found, try a dedicated case study extraction
#             if not self._contains_case_studies(battlecards):
#                 print("No case studies found in initial analysis. Performing dedicated case study extraction...")
#                 case_studies_by_problem = self._extract_case_studies_for_problems(text, battlecards)
#                 battlecards = self._enhance_battlecards_with_case_studies(battlecards, case_studies_by_problem)
            
#             # Enhance battlecards with more detailed problem descriptions and differentiators
#             battlecards = self._enhance_battlecard_content(text, battlecards)
            
#             case_study_map = {}
#             for i, card in enumerate(battlecards):
#                 if "case_studies" in card and isinstance(card["case_studies"], list):
#                     for j, study in enumerate(card["case_studies"]):
#                         simple_study = re.sub(r'[^\w\s]', '', study.lower())
#                         simple_study = ' '.join(simple_study.split())
#                         if simple_study not in case_study_map:
#                             case_study_map[simple_study] = (i, j)

#             # Replace any duplicate case studies
#             # battlecards = self._replace_duplicate_case_studies(text, battlecards, case_study_map)

#             print(f"Final battlecard count after deduplication: {len(battlecards)}")

#             return battlecards

#         except Exception as e:
#             print(f"Perplexity API Error: {str(e)}")
#             return []

#     def _clean_content(self, text: str) -> str:
#         """Clean the content by removing meta-comments about word count."""
#         # Remove phrases about word count
#         cleaned = re.sub(r"That'?s\s+(?:about|around)\s+\d+\s+words\.?", "", text)
#         cleaned = re.sub(r"\(\s*\d+\s+words\s*\)", "", cleaned)
#         cleaned = re.sub(r"Word count:?\s*\d+", "", cleaned)
        
#         # Remove other meta-comments
#         cleaned = re.sub(r"Here'?s\s+(?:a|the)\s+(?:summary|description).*?:", "", cleaned)
#         cleaned = re.sub(r'[*]{2}', '', cleaned)
#         cleaned = re.sub(r'\[\d+\](?:\[\d+\])*', '', cleaned) # Remove reference indicators like [1], [2], etc.
#         cleaned = re.sub(r'\s{2,}', ' ', cleaned)  # Replace multiple spaces with single space
        
#         return cleaned.strip()

#     def _extract_potential_case_studies(self, text: str) -> List[str]:
#         """Extract potential case study paragraphs from the text."""
#         case_study_indicators = [
#             r"case study", r"success story", r"client", r"customer", 
#             r"implementation", r"achievement", r"testimonial", r"result",
#             r"improved", r"increased", r"reduced", r"saved", r"delivered",
#             r"deployed", r"implemented", r"enabled", r"ROI", r"partnership",
#             r"collaboration", r"project", r"engagement", r"solution"
#         ]
        
#         # Split text into paragraphs
#         paragraphs = text.split('\n')
#         potential_case_studies = []
        
#         for i, paragraph in enumerate(paragraphs):
#             # Skip very short paragraphs
#             if len(paragraph.split()) < 10:
#                 continue
                
#             # Check if paragraph contains case study indicators
#             if any(re.search(indicator, paragraph, re.IGNORECASE) for indicator in case_study_indicators):
#                 # Include context from surrounding paragraphs
#                 start = max(0, i-1)
#                 end = min(len(paragraphs), i+2)
#                 context = "\n".join(paragraphs[start:end])
#                 potential_case_studies.append(context)
        
#         return potential_case_studies

#     def _enhance_battlecard_content(self, original_text: str, battlecards: List[Dict]) -> List[Dict]:
#         """Enhance problem descriptions and differentiators for each battlecard."""
#         enhanced_battlecards = []
        
#         for card in battlecards:
#             problem_area = card.get("problem_area", "")
#             if not problem_area:
#                 enhanced_battlecards.append(card)
#                 continue
            
#             # Get case studies for this battlecard
#             case_studies = card.get("case_studies", [])
            
#             # Create context from case studies
#             case_studies_context = "\n".join(case_studies) if case_studies else ""
            
#             # Create a dedicated prompt for enhancing this battlecard
#             prompt = f"""
#             Enhance the following battlecard with more detailed problem description and differentiator.
            
#             Problem Area: {problem_area}
#             Current Problem Description: {card.get('problem_description', '')}
#             Current Differentiator: {card.get('differentiator', '')}
            
#             Related Case Studies:
#             {case_studies_context}
            
#             Create an enhanced version with:
#             1. A more detailed problem description ( 100 words) that provides deep context about the challenges
#             2. A more comprehensive differentiator ( 100 words) that highlights unique value propositions
            
#             Make sure the content directly relates to the case studies if available, and provides specific, substantive details.
#             DO NOT include any comments about word count in your response.
            
#             Original text for reference:
#             {original_text[:5000]}
#             """
            
#             try:
#                 payload = {
#                     "model": "sonar-reasoning",
#                     "messages": [{"role": "user", "content": prompt}],
#                     "temperature": 0.7,
#                     "max_tokens": 1000
#                 }
                
#                 response = requests.post(
#                     self.base_url,
#                     headers=self.headers,
#                     json=payload
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     content = result["choices"][0]["message"]["content"]
                    
#                     # Extract enhanced description and differentiator
#                     description_match = re.search(r'Problem Description:(.*?)(?:Differentiator:|$)', content, re.DOTALL)
#                     differentiator_match = re.search(r'Differentiator:(.*?)$', content, re.DOTALL)
                    
#                     if description_match:
#                         enhanced_description = self._clean_content(description_match.group(1))
#                         card["problem_description"] = enhanced_description
                    
#                     if differentiator_match:
#                         enhanced_differentiator = self._clean_content(differentiator_match.group(1))
#                         card["differentiator"] = enhanced_differentiator
            
#             except Exception as e:
#                 print(f"Error enhancing battlecard for {problem_area}: {str(e)}")
            
#             enhanced_battlecards.append(card)
        
#         return enhanced_battlecards

#     def _contains_case_studies(self, battlecards: List[Dict]) -> bool:
#         """Check if battlecards contain any non-empty case studies."""
#         for card in battlecards:
#             case_studies = card.get("case_studies", [])
#             if case_studies and any(study for study in case_studies if study):
#                 return True
#         return False

#     def _extract_case_studies_for_problems(self, text: str, battlecards: List[Dict]) -> Dict[str, List[str]]:
#         """Perform a dedicated extraction of case studies for each problem area."""
#         case_studies_by_problem = {}
        
#         for card in battlecards:
#             problem_area = card.get("problem_area", "")
#             if not problem_area:
#                 continue
                
#             # Create a dedicated prompt for this problem area
#             prompt = f"""
#             From the following text, extract ONLY real case studies or success stories related to this specific problem area:
            
#             PROBLEM AREA: {problem_area}
            
#             Focus on:
#             - Client success stories for this problem
#             - Examples of implemented solutions for this issue
#             - Results achieved with specific customers
#             - Testimonials from customers about this problem area
            
#             Format your response as a JSON list of case study summaries.
#             Only include actual case studies, not general capabilities or features.
            
#             Text to analyze:
#             {text}
#             """
            
#             try:
#                 payload = {
#                     "model": "reasoning",
#                     "messages": [{"role": "user", "content": prompt}],
#                     "temperature": 0.7,
#                     "max_tokens": 1000
#                 }
                
#                 response = requests.post(
#                     self.base_url,
#                     headers=self.headers,
#                     json=payload
#                 )
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     content = result["choices"][0]["message"]["content"]
                    
#                     # Try to parse as JSON
#                     try:
#                         # Find JSON array in the content
#                         json_match = re.search(r'\[.*\]', content, re.DOTALL)
#                         if json_match:
#                             case_studies = json.loads(json_match.group(0))
#                             if isinstance(case_studies, list) and case_studies:
#                                 case_studies_by_problem[problem_area] = case_studies
#                     except json.JSONDecodeError:
#                         # If JSON parsing fails, try to extract case studies using regex
#                         studies = re.findall(r'"([^"]+)"', content)
#                         if studies:
#                             case_studies_by_problem[problem_area] = studies
            
#             except Exception as e:
#                 print(f"Error extracting case studies for {problem_area}: {str(e)}")
        
#         return case_studies_by_problem

#     def _enhance_battlecards_with_case_studies(self, battlecards: List[Dict], 
#                                               case_studies_by_problem: Dict[str, List[str]]) -> List[Dict]:
#         """Add extracted case studies to the battlecards."""
#         for card in battlecards:
#             problem_area = card.get("problem_area", "")
#             if problem_area in case_studies_by_problem:
#                 card["case_studies"] = case_studies_by_problem[problem_area]
        
#         return battlecards
    
#     # def _deduplicate_case_studies(self, battlecards: List[Dict]) -> List[Dict]:
#     #     """Remove duplicate case studies across different battlecards."""
#     #     # Create a dictionary to track all case studies
#     #     all_case_studies = {}  # Maps case study text -> (battlecard_index, case_study_index)
        
#     #     # First pass: identify duplicates
#     #     for i, card in enumerate(battlecards):
#     #         if "case_studies" not in card or not isinstance(card["case_studies"], list):
#     #             continue
                
#     #         # Store cleaned and normalized versions for comparison
#     #         card["case_studies"] = [self._clean_content(study) for study in card["case_studies"]]
            
#     #         filtered_studies = []
#     #         for j, study in enumerate(card["case_studies"]):
#     #             # Create a simplified version for comparison (lowercase, remove punctuation)
#     #             simple_study = re.sub(r'[^\w\s]', '', study.lower())
#     #             simple_study = ' '.join(simple_study.split())
                
#     #             # If this is a new case study or the first occurrence, keep it
#     #             if simple_study not in all_case_studies:
#     #                 all_case_studies[simple_study] = (i, j)
#     #                 filtered_studies.append(study)
#     #             elif all_case_studies[simple_study][0] == i:
#     #                 # This is a duplicate within the same battlecard, keep just one
#     #                 continue
#     #             else:
#     #                 # This is a duplicate from another battlecard, we'll address it in second pass
#     #                 all_case_studies[simple_study + f"_dup_{i}_{j}"] = (i, j)
#     #                 filtered_studies.append(study)
            
#     #         card["case_studies"] = filtered_studies
        
#     #     # Second pass: for cards with duplicate case studies, try to extract new ones
#     #     return battlecards
    
#     # def _replace_duplicate_case_studies(self, text: str, battlecards: List[Dict], case_study_map: Dict) -> List[Dict]:
#     #     """Generate replacement case studies for duplicates."""
#     #     for i, card in enumerate(battlecards):
#     #         if "case_studies" not in card or not card["case_studies"]:
#     #             continue
                
#     #         # Check if this card needs replacement case studies
#     #         needs_replacement = False
#     #         for study in card["case_studies"]:
#     #             simple_study = re.sub(r'[^\w\s]', '', study.lower())
#     #             simple_study = ' '.join(simple_study.split())
#     #             if simple_study in case_study_map and case_study_map[simple_study][0] != i:
#     #                 needs_replacement = True
#     #                 break
                    
#     #         if needs_replacement:
#     #             problem_area = card.get("problem_area", "")
#     #             prompt = f"""
#     #             Extract ONE specific case study for this problem area that's completely DIFFERENT from the existing ones:
                
#     #             PROBLEM AREA: {problem_area}
                
#     #             DO NOT repeat or paraphrase these existing case studies:
#     #             {', '.join(card["case_studies"])}
                
#     #             Focus on finding a DIFFERENT:
#     #             - Client success story for this problem
#     #             - Example of implemented solution for this issue
#     #             - Results achieved with a different customer
                
#     #             Provide just the case study text with no additional explanation.
#     #             If no distinct case study exists, respond with "No additional unique case studies found."
                
#     #             Text to analyze:
#     #             {text[:8000]}
#     #             """
                
#     #             try:
#     #                 payload = {
#     #                     "model": "sonar-reasoning", 
#     #                     "messages": [{"role": "user", "content": prompt}],
#     #                     "temperature": 0.7,
#     #                     "max_tokens": 800
#     #                 }
                    
#     #                 response = requests.post(
#     #                     self.base_url,
#     #                     headers=self.headers,
#     #                     json=payload
#     #                 )
                    
#     #                 if response.status_code == 200:
#     #                     result = response.json()
#     #                     content = result["choices"][0]["message"]["content"].strip()
                        
#     #                     if content and "No additional unique case studies found" not in content:
#     #                         # Replace the duplicate case studies with the new unique one
#     #                         unique_studies = []
#     #                         for study in card["case_studies"]:
#     #                             simple_study = re.sub(r'[^\w\s]', '', study.lower())
#     #                             simple_study = ' '.join(simple_study.split())
                                
#     #                             if simple_study in case_study_map and case_study_map[simple_study][0] != i:
#     #                                 # This is a duplicate from another card, replace it
#     #                                 if content and content not in unique_studies:
#     #                                     unique_studies.append(self._clean_content(content))
#     #                                     content = ""  # Only use the new content once
#     #                             else:
#     #                                 # Keep original non-duplicate case study
#     #                                 unique_studies.append(study)
                                    
#     #                         card["case_studies"] = unique_studies
                
#     #             except Exception as e:
#     #                 print(f"Error replacing duplicate case studies for {problem_area}: {str(e)}")
        
#     #     return battlecards

#     def _parse_response(self, content: str) -> List[Dict]:
#         """Enhanced JSON parsing with better error handling and repair attempts."""
#         # First, try to find JSON in the response
#         try:
#             # Check if the entire content is valid JSON
#             try:
#                 return json.loads(content)
#             except json.JSONDecodeError:
#                 pass
                
#             # Try to extract just the JSON array
#             json_array_match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
#             if json_array_match:
#                 json_str = json_array_match.group(0)
#                 return json.loads(json_str)
                
#             # If that fails, look for markers and try to extract
#             start_idx = content.find('[')
#             end_idx = content.rfind(']') + 1
            
#             if start_idx >= 0 and end_idx > start_idx:
#                 json_str = content[start_idx:end_idx]
#                 try:
#                     return json.loads(json_str)
#                 except json.JSONDecodeError as e:
#                     print(f"JSON error: {e}")
#                     # Attempt to repair common JSON issues
#                     repaired_json = self._repair_json(json_str)
#                     return json.loads(repaired_json)
                
#         except Exception as e:
#             print(f"Enhanced JSON parsing failed: {e}")
            
#         # If all parsing attempts fail, use fallback parsing
#         print("JSON parsing failed, using fallback parser")
#         return self._fallback_parsing(content)

#     def _fallback_parsing(self, content: str) -> List[Dict]:
#         """
#         Fallback method to parse non-JSON formatted responses.
#         """
#         print("Using fallback parsing for response:", content[:100])
#         battlecards = []
#         current_card = {}
#         case_studies = []
        
#         lines = content.split('\n')
#         for line in lines:
#             line = line.strip()
#             if not line:
#                 continue
                
#             if "Problem Area:" in line or "Need:" in line:
#                 if current_card and 'problem_area' in current_card:
#                     if case_studies:
#                         current_card["case_studies"] = case_studies
#                     battlecards.append(current_card)
#                     case_studies = []
#                 current_card = {"problem_area": line.split(":", 1)[1].strip()}
#             elif "Problem Description:" in line:
#                 current_card["problem_description"] = self._clean_content(line.split(":", 1)[1].strip())
#             elif "Solution:" in line or "Differentiator:" in line:
#                 current_card["differentiator"] = self._clean_content(line.split(":", 1)[1].strip())
#             elif "Case Study:" in line or "Case Studies:" in line:
#                 case_study = self._clean_content(line.split(":", 1)[1].strip())
#                 case_studies.append(case_study)
#             # Also catch numbered case studies
#             elif re.match(r'^\d+\.\s+Case Study:', line):
#                 case_study = self._clean_content(line.split(":", 1)[1].strip())
#                 case_studies.append(case_study)
#             elif re.match(r'^\d+\.\s+', line) and current_card and 'case_studies' in current_card:
#                 # This might be a numbered case study without explicit labeling
#                 case_studies.append(self._clean_content(line))

#         if current_card and 'problem_area' in current_card:
#             if case_studies:
#                 current_card["case_studies"] = case_studies
#             battlecards.append(current_card)

#         # If we couldn't parse anything, create a default battlecard
#         if not battlecards:
#             battlecards = [{
#                 "problem_area": "Content Analysis",
#                 "problem_description": "The content was analyzed but couldn't be structured into specific battlecards.",
#                 "differentiator": "Consider reviewing the text manually and identifying key problems and solutions.",
#                 "case_studies": []
#             }]

#         return battlecards


import requests
import json
from typing import List, Dict, Optional
import re

class PerplexityAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def analyze_text(self, text: str) -> List[Dict]:
        """
        Analyze text using Perplexity AI to generate battlecards.
        """
        # # Truncate text if it's too long
        # max_text_length = 15000
        # if len(text) > max_text_length:
        #     text = text[:max_text_length]
        
        # First, extract potential case studies from the text
        case_studies = self._extract_potential_case_studies(text)
        case_studies_str = "\n\n".join(case_studies) if case_studies else "No explicit case studies found."
        
        prompt = f"""
        Analyze the following text and generate comprehensive battlecards. 
        Each battlecard should contain:
        1. A specific problem area or need that the company/product addresses
        2. A detailed problem description (up to 100 words) that explains the challenge faced by clients
        3. Solutions and differentiators (up to 100 words) that highlight unique value propositions
        4. Case studies that demonstrate the solution in real-world scenarios

        Pay special attention to these POTENTIAL CASE STUDIES found in the text:
        {case_studies_str}

        Format the response as a JSON array of battlecards with these exact keys:
        [
            {{
                "problem_area": "Problem area title",
                "problem_description": "Thorough explanation of the problem",
                "differentiator": "Detailed solution and unique value proposition",
                "case_studies": ["Case study 1", "Case study 2"]
            }}
        ]

        IMPORTANT GUIDELINES:
        - The problem description should directly relate to the case studies and provide context for them
        - Make differentiators specific and substantive, avoiding vague marketing language
        - Don't include comments about word count in your response
        - Ensure case studies include specific results, clients, or implementations whenever possible
        - Focus on quality over quantity - it's better to have fewer, well-developed battlecards than many shallow ones

        Text to analyze:
        {text}
        """

        try:
            payload = {
                "model": "sonar-reasoning",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 3000
            }
            
            print("Sending request to Perplexity API...")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code} - {response.text}")
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
            result = response.json()
            
            # Extract and parse the battlecards from the response
            content = result["choices"][0]["message"]["content"]
            battlecards = self._parse_response(content)
            
            # If no case studies were found, try a dedicated case study extraction
            if not self._contains_case_studies(battlecards):
                print("No case studies found in initial analysis. Performing dedicated case study extraction...")
                case_studies_by_problem = self._extract_case_studies_for_problems(text, battlecards)
                battlecards = self._enhance_battlecards_with_case_studies(battlecards, case_studies_by_problem)
            
            # Enhance battlecards with more detailed problem descriptions and differentiators
            battlecards = self._enhance_battlecard_content(text, battlecards)
            
            return battlecards

        except Exception as e:
            print(f"Perplexity API Error: {str(e)}")
            return []

    def _clean_content(self, text: str) -> str:
        """Clean the content by removing meta-comments about word count."""
        # Remove phrases about word count
        cleaned = re.sub(r"That'?s\s+(?:about|around)\s+\d+\s+words\.?", "", text)
        cleaned = re.sub(r"\(\s*\d+\s+words\s*\)", "", cleaned)
        cleaned = re.sub(r"Word count:?\s*\d+", "", cleaned)
        
        # Remove other meta-comments
        cleaned = re.sub(r"Here'?s\s+(?:a|the)\s+(?:summary|description).*?:", "", cleaned)
        cleaned = re.sub(r'[*]{2}', '', cleaned)
        cleaned = re.sub(r'\[\d+\](?:\[\d+\])*', '', cleaned) # Remove reference indicators like [1], [2], etc.
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)  # Replace multiple spaces with single space
        
        return cleaned.strip()

    def _extract_potential_case_studies(self, text: str) -> List[str]:
        """Extract potential case study paragraphs from the text."""
        case_study_indicators = [
            r"case study", r"success story", r"client", r"customer", 
            r"implementation", r"achievement", r"testimonial", r"result",
            r"improved", r"increased", r"reduced", r"saved", r"delivered",
            r"deployed", r"implemented", r"enabled", r"ROI", r"partnership",
            r"collaboration", r"project", r"engagement", r"solution"
        ]
        
        # Split text into paragraphs
        paragraphs = text.split('\n')
        potential_case_studies = []
        
        for i, paragraph in enumerate(paragraphs):
            # Skip very short paragraphs
            if len(paragraph.split()) < 10:
                continue
                
            # Check if paragraph contains case study indicators
            if any(re.search(indicator, paragraph, re.IGNORECASE) for indicator in case_study_indicators):
                # Include context from surrounding paragraphs
                start = max(0, i-1)
                end = min(len(paragraphs), i+2)
                context = "\n".join(paragraphs[start:end])
                potential_case_studies.append(context)
        
        return potential_case_studies

    def _enhance_battlecard_content(self, original_text: str, battlecards: List[Dict]) -> List[Dict]:
        """Enhance problem descriptions and differentiators for each battlecard."""
        enhanced_battlecards = []
        
        for card in battlecards:
            problem_area = card.get("problem_area", "")
            if not problem_area:
                enhanced_battlecards.append(card)
                continue
            
            # Get case studies for this battlecard
            case_studies = card.get("case_studies", [])
            
            # Create context from case studies
            case_studies_context = "\n".join(case_studies) if case_studies else ""
            
            # Create a dedicated prompt for enhancing this battlecard
            prompt = f"""
            Enhance the following battlecard with more detailed problem description and differentiator.
            
            Problem Area: {problem_area}
            Current Problem Description: {card.get('problem_description', '')}
            Current Differentiator: {card.get('differentiator', '')}
            
            Related Case Studies:
            {case_studies_context}
            
            Create an enhanced version with:
            1. A more detailed problem description (up to 100 words) that provides deep context about the challenges
            2. A more comprehensive differentiator (up to 100 words) that highlights unique value propositions
            
            Make sure the content directly relates to the case studies if available, and provides specific, substantive details.
            DO NOT include any comments about word count in your response.
            
            Original text for reference:
            {original_text[:5000]}
            """
            
            try:
                payload = {
                    "model": "llama-3.1-sonar-huge-128k-online",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Extract enhanced description and differentiator
                    description_match = re.search(r'Problem Description:(.*?)(?:Differentiator:|$)', content, re.DOTALL)
                    differentiator_match = re.search(r'Differentiator:(.*?)$', content, re.DOTALL)
                    
                    if description_match:
                        enhanced_description = self._clean_content(description_match.group(1))
                        card["problem_description"] = enhanced_description
                    
                    if differentiator_match:
                        enhanced_differentiator = self._clean_content(differentiator_match.group(1))
                        card["differentiator"] = enhanced_differentiator
            
            except Exception as e:
                print(f"Error enhancing battlecard for {problem_area}: {str(e)}")
            
            enhanced_battlecards.append(card)
        
        return enhanced_battlecards

    def _contains_case_studies(self, battlecards: List[Dict]) -> bool:
        """Check if battlecards contain any non-empty case studies."""
        for card in battlecards:
            case_studies = card.get("case_studies", [])
            if case_studies and any(study for study in case_studies if study):
                return True
        return False

    def _extract_case_studies_for_problems(self, text: str, battlecards: List[Dict]) -> Dict[str, List[str]]:
        """Perform a dedicated extraction of case studies for each problem area."""
        case_studies_by_problem = {}
        
        for card in battlecards:
            problem_area = card.get("problem_area", "")
            if not problem_area:
                continue
                
            # Create a dedicated prompt for this problem area
            prompt = f"""
            From the following text, extract ONLY real case studies or success stories related to this specific problem area:
            
            PROBLEM AREA: {problem_area}
            
            Focus on:
            - Client success stories for this problem
            - Examples of implemented solutions for this issue
            - Results achieved with specific customers
            - Testimonials from customers about this problem area
            
            Format your response as a JSON list of case study summaries.
            Only include actual case studies, not general capabilities or features.
            
            Text to analyze:
            {text}
            """
            
            try:
                payload = {
                    "model": "llama-3.1-sonar-huge-128k-online",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Try to parse as JSON
                    try:
                        # Find JSON array in the content
                        json_match = re.search(r'\[.*\]', content, re.DOTALL)
                        if json_match:
                            case_studies = json.loads(json_match.group(0))
                            if isinstance(case_studies, list) and case_studies:
                                case_studies_by_problem[problem_area] = case_studies
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract case studies using regex
                        studies = re.findall(r'"([^"]+)"', content)
                        if studies:
                            case_studies_by_problem[problem_area] = studies
            
            except Exception as e:
                print(f"Error extracting case studies for {problem_area}: {str(e)}")
        
        return case_studies_by_problem

    def _enhance_battlecards_with_case_studies(self, battlecards: List[Dict], 
                                              case_studies_by_problem: Dict[str, List[str]]) -> List[Dict]:
        """Add extracted case studies to the battlecards."""
        for card in battlecards:
            problem_area = card.get("problem_area", "")
            if problem_area in case_studies_by_problem:
                card["case_studies"] = case_studies_by_problem[problem_area]
        
        return battlecards

    def _parse_response(self, content: str) -> List[Dict]:
        """
        Parse the API response and format it into battlecards.
        """
        try:
            # Try to find JSON in the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                battlecards = json.loads(json_str)
                
                # Clean content for each battlecard
                for card in battlecards:
                    if "problem_description" in card:
                        card["problem_description"] = self._clean_content(card["problem_description"])
                    if "differentiator" in card:
                        card["differentiator"] = self._clean_content(card["differentiator"])
                    if "case_studies" in card and isinstance(card["case_studies"], list):
                        card["case_studies"] = [self._clean_content(study) for study in card["case_studies"]]
                
                return battlecards
            else:
                return self._fallback_parsing(content)
                
        except json.JSONDecodeError:
            print("JSON parsing failed, using fallback parser")
            return self._fallback_parsing(content)

    def _fallback_parsing(self, content: str) -> List[Dict]:
        """
        Fallback method to parse non-JSON formatted responses.
        """
        print("Using fallback parsing for response:", content[:100])
        battlecards = []
        current_card = {}
        case_studies = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "Problem Area:" in line or "Need:" in line:
                if current_card and 'problem_area' in current_card:
                    if case_studies:
                        current_card["case_studies"] = case_studies
                    battlecards.append(current_card)
                    case_studies = []
                current_card = {"problem_area": line.split(":", 1)[1].strip()}
            elif "Problem Description:" in line:
                current_card["problem_description"] = self._clean_content(line.split(":", 1)[1].strip())
            elif "Solution:" in line or "Differentiator:" in line:
                current_card["differentiator"] = self._clean_content(line.split(":", 1)[1].strip())
            elif "Case Study:" in line or "Case Studies:" in line:
                case_study = self._clean_content(line.split(":", 1)[1].strip())
                case_studies.append(case_study)
            # Also catch numbered case studies
            elif re.match(r'^\d+\.\s+Case Study:', line):
                case_study = self._clean_content(line.split(":", 1)[1].strip())
                case_studies.append(case_study)
            elif re.match(r'^\d+\.\s+', line) and current_card and 'case_studies' in current_card:
                # This might be a numbered case study without explicit labeling
                case_studies.append(self._clean_content(line))

        if current_card and 'problem_area' in current_card:
            if case_studies:
                current_card["case_studies"] = case_studies
            battlecards.append(current_card)

        # If we couldn't parse anything, create a default battlecard
        if not battlecards:
            battlecards = [{
                "problem_area": "Content Analysis",
                "problem_description": "The content was analyzed but couldn't be structured into specific battlecards.",
                "differentiator": "Consider reviewing the text manually and identifying key problems and solutions.",
                "case_studies": []
            }]

        return battlecards