"""
ProposalBio™ Quality Assurance Module
10 Biohack Analysis Engine for Government Proposals
Dee Davis Inc - GPSS Integration
"""

import json
import math
import re
from datetime import datetime
from collections import Counter
from typing import Dict, List, Optional, Tuple

from nexus_backend import AirtableClient


BIOHACKS = {
    1: "Mirror Neuron",
    2: "Cognitive Ease",
    3: "Story Arc",
    4: "Reciprocity",
    5: "Yes Stacking",
    6: "Familiarity",
    7: "Name Recognition",
    8: "Sensory Language",
    9: "Rhythm",
    10: "Eye Tracking",
}


class ProposalBioAnalyzer:
    """Core analyzer implementing the 10 ProposalBio™ biohacks"""
    
    def __init__(self, proposal_text: str, metadata: Dict):
        self.text = proposal_text or ""
        self.meta = metadata or {}
        self.sentences = self._split_sentences(self.text)
        self.paragraphs = self._split_paragraphs(self.text)
        self.pages = max(1, len(self.text) // 2500)

    def analyze_all(self) -> Dict:
        """Run all 10 biohack analyses and return comprehensive results"""
        scores = {
            1: self.analyze_mirror_neuron(),
            2: self.analyze_cognitive_ease(),
            3: self.analyze_story_arc(),
            4: self.analyze_reciprocity(),
            5: self.analyze_yes_stacking(),
            6: self.analyze_familiarity(),
            7: self.analyze_name_recognition(),
            8: self.analyze_sensory_language(),
            9: self.analyze_rhythm(),
            10: self.analyze_eye_tracking(),
        }

        composite = sum(scores.values()) / 10.0 * 10.0  # Scale to 0-100
        status = self._determine_status(composite, scores)

        critical_issues = [
            {"biohack_number": n, "biohack_name": BIOHACKS[n], "score": s}
            for n, s in scores.items()
            if s < 6
        ]

        priority_improvements = self._priority_improvements(scores)

        return {
            "analysis_complete": True,
            "composite_score": round(composite, 2),
            "overall_status": status,
            "biohack_scores": [
                {
                    "biohack_number": n,
                    "biohack_name": BIOHACKS[n],
                    "score": float(round(scores[n], 2)),
                    "pass_fail": "Pass" if scores[n] >= 6 else "Fail",
                }
                for n in range(1, 11)
            ],
            "critical_issues": critical_issues,
            "priority_improvements": priority_improvements,
            "estimated_revision_time_minutes": self._estimate_revision_minutes(scores),
            "analyzed_timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # =====================================
    # BIOHACK ANALYZERS
    # =====================================

    def analyze_cognitive_ease(self) -> float:
        """Biohack #2: Simplicity is presence of clarity"""
        score = 0
        grade = self._flesch_kincaid_grade(self.text)
        avg_wps = self._avg_words_per_sentence()
        avg_spp = self._avg_sentences_per_paragraph()
        white = self._white_space_ratio()

        # Reading level (target: 6-8th grade)
        if 6 <= grade <= 8: score += 3
        elif grade <= 10: score += 2
        elif grade <= 12: score += 1

        # Words per sentence (target: ≤12)
        if avg_wps <= 12: score += 2

        # Sentences per paragraph (target: ≤10)
        if avg_spp <= 10: score += 2

        # One idea per paragraph
        if self._one_idea_per_paragraph(): score += 2

        # White space (target: ≥40%)
        if white >= 40: score += 1

        return min(10, score)

    def analyze_sensory_language(self) -> float:
        """Biohack #8: Paint with words - if they can't see it, they can't sign it"""
        vague_terms = [
            "quality","great","excellent","superior","best",
            "fast","quick","rapid","timely","prompt",
            "experienced","skilled","qualified","capable",
            "efficient","effective","optimal","streamlined",
            "innovative","cutting-edge","state-of-the-art",
            "comprehensive","robust","flexible","scalable",
            "proven","reliable","trusted","established",
            "dedicated","committed","focused",
        ]
        sensory = ["feel","seamless","smooth","clear","tangible","visible","concrete","measurable","experience","see"]

        vague_count = sum(len(re.findall(rf"\b{re.escape(t)}\b", self.text, re.I)) for t in vague_terms)
        sensory_count = sum(len(re.findall(rf"\b{re.escape(t)}\b", self.text, re.I)) for t in sensory)

        # Penalty for too many vague terms
        threshold = max(5, int(self.pages * 0.5))
        score = 10.0
        if vague_count > threshold:
            score -= (vague_count - threshold) * 0.5

        # Bonus for sensory language
        sensory_target = max(10, int(self.pages * 1.0))
        if sensory_count >= sensory_target:
            score += 1.5

        return float(max(0, min(10, score)))

    def analyze_name_recognition(self) -> float:
        """Biohack #7: Every executive's favorite sound is their own name"""
        agency = (self.meta.get("client_name") or self.meta.get("agency") or "").strip()
        if not agency:
            return 0.0

        name_count = len(re.findall(rf"\b{re.escape(agency)}\b", self.text, re.I))
        name_per_page = name_count / float(self.pages)

        score = 0
        if name_per_page >= 0.8: score += 3
        elif name_per_page >= 0.5: score += 2
        elif name_per_page >= 0.3: score += 1

        # Check for generic language (penalty)
        generic = sum(len(re.findall(p, self.text, re.I)) for p in [
            r"\byour organization\b", r"\byour agency\b", r"\byour department\b", r"\byour office\b"
        ])
        if generic == 0: score += 1

        # Check if agency name in headers
        if re.search(r"\bmission\b|\bvision\b|\bstrategic plan\b", self.text, re.I): 
            score += 2

        # Check mission/vision reference
        if re.search(rf"{re.escape(agency)}.*(mission|vision|strategic plan)", self.text, re.I): 
            score += 1

        return float(min(10, score))

    def analyze_familiarity(self) -> float:
        """Biohack #6: Echo their language back - speak their language, not yours"""
        rfp_text = (self.meta.get("rfp_text") or "").strip()
        if not rfp_text:
            return 5.0  # Neutral when RFP text not available

        rfp_terms = set(self._key_terms(rfp_text))
        prop_terms = set(self._key_terms(self.text))
        if not rfp_terms:
            return 5.0

        # Calculate mirroring percentage
        mirror = len(rfp_terms & prop_terms) / float(len(rfp_terms)) * 100.0
        score = 0
        if mirror >= 70: score += 3
        elif mirror >= 50: score += 2
        elif mirror >= 30: score += 1

        # Check if solicitation number referenced
        rfp_number = (self.meta.get("rfp_number") or "").strip()
        if rfp_number and re.search(re.escape(rfp_number), self.text): 
            score += 2

        # Check for consultant jargon (penalty)
        jargon = sum(len(re.findall(p, self.text, re.I)) for p in [
            r"\bsynergy\b", r"\bleverage\b", r"\bparadigm\b"
        ])
        if jargon == 0: score += 1

        # Check mission statement echo
        if re.search(r"\bmission\b|\bvision\b", self.text, re.I): 
            score += 2

        # Additional credit for good mirroring
        if mirror >= 60: score += 2

        return float(min(10, score))

    def analyze_yes_stacking(self) -> float:
        """Biohack #5: Stack the yes before you ask for it"""
        patterns = [
            r"\bwe agree\b", 
            r"\bwe share\b", 
            r"\bour values align\b", 
            r"\blike .* we believe\b", 
            r"\bcommitment to\b"
        ]
        affirm = sum(len(re.findall(p, self.text, re.I)) for p in patterns)

        score = 0
        if affirm >= 5: score += 3
        elif affirm >= 3: score += 2
        elif affirm >= 1: score += 1

        # Check positioning (before pricing)
        pricing_pos = min([m.start() for m in re.finditer(r"\b(pricing|cost|budget|price)\b", self.text, re.I)] or [10**9])
        agree_pos = [m.start() for m in re.finditer(r"\bwe agree\b", self.text, re.I)]
        if agree_pos and sum(1 for p in agree_pos if p < pricing_pos) >= max(1, int(len(agree_pos) * 0.7)):
            score += 2

        # Check for values alignment
        if re.search(r"\bour values align\b|\bshared values\b|\bcommitment\b", self.text, re.I):
            score += 2

        # Variety check
        if affirm >= 3: score += 2

        # Momentum bonus
        if score >= 7: score += 1

        return float(min(10, score))

    def analyze_reciprocity(self) -> float:
        """Biohack #4: Give before you gain - value travels faster when it moves first"""
        # Detect give-first content
        value_add = sum(len(re.findall(p, self.text, re.I)) for p in [
            r"\bchecklist\b", r"\bframework\b", r"\bbenchmark\b", 
            r"\binsight\b", r"\bappendix\b", r"\bwhite paper\b", r"\banalysis\b"
        ])
        
        # Check for ADA violations (offering free services)
        ada_violation = sum(len(re.findall(p, self.text, re.I)) for p in [
            r"\bfree service\b", r"\bno-cost service\b"
        ])

        score = 0
        if value_add >= 2: score += 3
        elif value_add >= 1: score += 2

        # Check for statistics/insights
        stats = len(re.findall(r"\b\d+%|\$\d+", self.text))
        if stats >= self.pages * 2: score += 2
        elif stats >= self.pages: score += 1

        # Check for educational content
        edu = sum(len(re.findall(p, self.text, re.I)) for p in [
            r"\bbest practice\b", r"\bguide\b", r"\bhow to\b"
        ])
        if edu >= 2: score += 2
        elif edu >= 1: score += 1

        # ADA compliance check
        if ada_violation == 0: 
            score += 1
        else: 
            score -= 5  # Major penalty

        return float(max(0, min(10, score)))

    def analyze_story_arc(self) -> float:
        """Biohack #3: Stories transform - logic gets in door, emotion gets the deal"""
        challenge = [r"\bchallenge\b", r"\bproblem\b", r"\bfaced\b", r"\bissue\b"]
        solution = [r"\bimplemented\b", r"\bapproach\b", r"\bsolution\b", r"\bwe guided\b"]
        result = [r"\bachieved\b", r"\boutcome\b", r"\bresult\b", r"\b\d+%|\$\d+"]

        sents = self.sentences
        stories = 0
        for i in range(0, max(0, len(sents) - 8)):
            window = " ".join(sents[i:i+9])
            if (any(re.search(p, window, re.I) for p in challenge) and
                any(re.search(p, window, re.I) for p in solution) and
                any(re.search(p, window, re.I) for p in result)):
                stories += 1

        score = 0
        if stories >= 3: score += 3
        elif stories >= 2: score += 2
        elif stories >= 1: score += 1

        # Check positioning (company as guide, not hero)
        if re.search(r"\bwe are the best\b|\bnumber one\b", self.text, re.I):
            pass  # No bonus
        else:
            score += 2

        # Check for metrics
        if re.search(r"\b\d+%|\$\d+", self.text): 
            score += 1

        # Story structure completeness
        if stories >= 2: score += 2

        # RFP relevance (basic check)
        if stories >= 1: score += 2

        return float(min(10, score))

    def analyze_rhythm(self) -> float:
        """Biohack #9: Brain loves rhythm more than reason"""
        lens = [len(s.split()) for s in self.sentences if s.strip()]
        if not lens:
            return 0.0
        
        avg = sum(lens)/len(lens)
        score = 0
        
        # Average sentence length
        if 10 <= avg <= 15: score += 2
        elif 8 <= avg <= 17: score += 1

        # Sentence variation (standard deviation)
        if len(lens) > 1:
            mean = avg
            var = sum((x-mean)**2 for x in lens)/(len(lens)-1)
            std = math.sqrt(var)
            variation = min(10.0, (std / max(1.0, mean)) * 20.0)
            if variation >= 7: score += 2
            elif variation >= 5: score += 1

        # Check for monotone sections
        monotone = 0
        for i in range(len(lens)-2):
            w = lens[i:i+3]
            if max(w)-min(w) <= 2:
                monotone += 1
        if monotone == 0: score += 2
        elif monotone <= len(lens)*0.1: score += 1

        # One-liners (sentences ≤6 words)
        one_liners = sum(1 for x in lens if x <= 6)
        if one_liners >= self.pages * 0.5: score += 2
        elif one_liners >= self.pages * 0.3: score += 1

        # Cadence breaks (long followed by short)
        breaks = sum(1 for i in range(len(lens)-1) if lens[i] > 20 and lens[i+1] <= 6)
        if breaks >= self.pages * 0.3: score += 2

        return float(min(10, score))

    def analyze_eye_tracking(self) -> float:
        """Biohack #10: Eyes get lost, deal is lost"""
        score = 0
        
        # Headings (short all-caps lines)
        headings = len(re.findall(r"(^|\n)[A-Z0-9 \-]{8,60}(\n|$)", self.text))
        if headings >= self.pages: score += 2
        elif headings >= self.pages * 0.7: score += 1

        # Visual elements
        visuals = sum(len(re.findall(p, self.text, re.I)) for p in [
            r"\bfigure\b", r"\bchart\b", r"\bdiagram\b", r"\btable\b", r"\bexhibit\b"
        ])
        if visuals >= max(1, int(self.pages/2.5)): score += 2
        elif visuals >= 1: score += 1

        # Section summaries
        summaries = sum(len(re.findall(p, self.text, re.I)) for p in [
            r"\bin summary\b", r"\bto summarize\b", r"\bkey points\b", r"\bsummary:\b"
        ])
        if summaries >= max(1, int(self.pages/2)): score += 2
        elif summaries >= 1: score += 1

        # White space
        white = self._white_space_ratio()
        if white >= 40: score += 2
        elif white >= 30: score += 1

        # Visual hierarchy (bullets + numbering)
        bullets = len(re.findall(r"(^|\n)\s*[-•]\s+", self.text))
        nums = len(re.findall(r"(^|\n)\s*\d+\.\s+", self.text))
        if (bullets + nums) >= self.pages * 5: score += 2
        elif (bullets + nums) >= self.pages * 2: score += 1

        return float(min(10, score))

    def analyze_mirror_neuron(self) -> float:
        """Biohack #1: Feel like me, think like me - highest level of bio-influence"""
        region = (self.meta.get("region") or "").strip()
        agency_type = (self.meta.get("agency_type") or "").strip()

        if not region:
            return 5.0  # Neutral if unknown

        # Formality markers
        formal_markers = ["in accordance with", "pursuant to", "as prescribed", "compliance with"]
        casual_markers = ["we're", "it's", "that's", "let's"]

        formal = sum(len(re.findall(re.escape(p), self.text, re.I)) for p in formal_markers)
        casual = sum(len(re.findall(re.escape(p), self.text, re.I)) for p in casual_markers)
        ratio = formal / float(max(1, formal + casual))

        # Expected formality by agency type
        target = {"Federal": 0.8, "State": 0.5, "Local": 0.3, "Cooperative": 0.4}.get(agency_type, 0.5)
        score = 0

        if abs(ratio - target) < 0.2: score += 2
        else: score += 1

        # Regional phrase matching
        region_hints = {
            "Mid_Atlantic": ["in accordance", "pursuant to", "compliance"],
            "Northeast": ["bottom line", "here's what matters", "results"],
            "Southeast": ["partnership", "community", "commitment"],
            "Midwest": ["reliable", "track record", "proven results"],
            "Southwest": ["results-driven", "commitment to excellence", "track record"],
            "West_Coast": ["collaborative", "innovation", "sustainable solutions"],
        }
        hits = sum(len(re.findall(re.escape(p), self.text, re.I)) for p in region_hints.get(region, []))
        if hits >= 2: score += 3
        elif hits >= 1: score += 2
        else: score += 1

        # Mismatch penalty
        if agency_type == "Federal" and ratio < 0.5:
            score -= 1

        return float(max(0, min(10, score)))

    # =====================================
    # HELPER METHODS
    # =====================================

    def _split_sentences(self, text: str) -> List[str]:
        parts = re.split(r"[.!?]+\s+", text)
        return [p.strip() for p in parts if p.strip()]

    def _split_paragraphs(self, text: str) -> List[str]:
        parts = re.split(r"\n\s*\n", text)
        return [p.strip() for p in parts if p.strip()]

    def _avg_words_per_sentence(self) -> float:
        if not self.sentences:
            return 0.0
        words = re.findall(r"\b\w+\b", self.text)
        return len(words) / float(len(self.sentences))

    def _avg_sentences_per_paragraph(self) -> float:
        if not self.paragraphs:
            return 0.0
        return len(self.sentences) / float(len(self.paragraphs))

    def _white_space_ratio(self) -> float:
        total = len(self.text)
        if total <= 0:
            return 0.0
        non = len(self.text.replace(" ", "").replace("\n", "").replace("\t", ""))
        return (total - non) / float(total) * 100.0

    def _one_idea_per_paragraph(self) -> bool:
        long_paras = [p for p in self.paragraphs if len(p.split()) > 200]
        return len(long_paras) <= max(1, int(len(self.paragraphs) * 0.2))

    def _count_syllables(self, text: str) -> int:
        vowels = "aeiouy"
        words = re.findall(r"\b\w+\b", text.lower())
        total = 0
        for w in words:
            count = 0
            prev = False
            for ch in w:
                is_v = ch in vowels
                if is_v and not prev:
                    count += 1
                prev = is_v
            if w.endswith("e") and count > 1:
                count -= 1
            total += max(1, count)
        return total

    def _flesch_kincaid_grade(self, text: str) -> float:
        sents = max(1, len(self.sentences))
        words = re.findall(r"\b\w+\b", text)
        if not words:
            return 0.0
        syll = self._count_syllables(text)
        return max(0.0, 0.39 * (len(words)/sents) + 11.8 * (syll/len(words)) - 15.59)

    def _key_terms(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        stop = {"that","this","with","from","have","been","were","will","your","their","about","which","when","where","there","would","could","should","these","those","them","then"}
        words = [w for w in words if w not in stop]
        freq = Counter(words)
        return [w for (w, _) in freq.most_common(50)]

    def _determine_status(self, composite: float, scores: Dict[int, float]) -> str:
        """Determine overall status: APPROVED / REVISE / REDRAFT / REJECT"""
        if any(s < 6 for s in scores.values()):
            return "REJECT" if composite < 60 else "REDRAFT"
        if composite >= 90: return "APPROVED"
        if composite >= 75: return "REVISE"
        if composite >= 60: return "REDRAFT"
        return "REJECT"

    def _priority_improvements(self, scores: Dict[int, float]) -> List[Dict]:
        """Generate ranked list of improvements"""
        items = []
        for n, s in scores.items():
            if s < 6:
                impact = "High"
            elif s < 8:
                impact = "Medium"
            else:
                continue
            items.append({
                "impact": impact, 
                "biohack_number": n, 
                "biohack_name": BIOHACKS[n], 
                "score": float(s)
            })
        items.sort(key=lambda x: (0 if x["impact"] == "High" else 1, x["score"]))
        for i, it in enumerate(items, 1):
            it["rank"] = i
            it["estimated_time_minutes"] = 30 if it["impact"] == "High" else 15
        return items[:10]

    def _estimate_revision_minutes(self, scores: Dict[int, float]) -> int:
        """Estimate total revision time"""
        mins = 0
        for s in scores.values():
            if s < 6: mins += 45
            elif s < 8: mins += 20
        return mins


class ProposalBioService:
    """Service layer for ProposalBio™ operations"""
    
    def __init__(self):
        self.airtable = AirtableClient()

    def analyze_proposal(self, proposal_id: str, metadata_override: Optional[Dict] = None) -> Dict:
        """
        Analyze a proposal from Airtable and update with ProposalBio scores
        
        Args:
            proposal_id: Airtable record ID
            metadata_override: Optional metadata to override/supplement
            
        Returns:
            Analysis results with scores, status, and gate decision
        """
        proposal = self._get_record_by_id("GPSS Proposals", proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}

        fields = proposal.get("fields", {})
        proposal_text = self._build_proposal_text(fields)

        # Build metadata
        meta = {
            "proposal_id": proposal_id,
            "proposal_name": fields.get("PROPOSAL NAME", ""),
            "rfp_number": fields.get("RFP NUMBER", ""),
            "agency": fields.get("AGENCY NAME", ""),
            "client_name": fields.get("AGENCY NAME", ""),
            "agency_type": (fields.get("AGENCY TYPE") or ""),
            "region": (fields.get("REGION") or ""),
            "rfp_text": (fields.get("RFP TEXT") or ""),
        }
        if metadata_override:
            meta.update(metadata_override)

        # Run analysis
        analyzer = ProposalBioAnalyzer(proposal_text, meta)
        result = analyzer.analyze_all()

        # Gate decision
        gate = "UNLOCKED" if (result["composite_score"] >= 75 and not result["critical_issues"]) else "LOCKED"

        # Update proposal record
        update_fields = {
            "PROPOSALBIO COMPOSITE SCORE": result["composite_score"],
            "PROPOSALBIO STATUS": result["overall_status"],
            "PROPOSALBIO LAST ANALYZED": result["analyzed_timestamp"],
            "PROPOSALBIO GATE": gate,
            "PROPOSALBIO BIOHACK SCORE JSON": json.dumps(result["biohack_scores"]),
            "PROPOSALBIO CRITICAL ISSUES JSON": json.dumps(result["critical_issues"]),
            "PROPOSALBIO PRIORITY IMPROVEMENT JSON": json.dumps(result["priority_improvements"]),
        }
        self.airtable.update_record("GPSS Proposals", proposal_id, update_fields)

        # Write per-biohack scores to separate table
        try:
            revision = int(fields.get("PROPOSAL REVISION COURT") or 0) + 1
            for bh in result["biohack_scores"]:
                self.airtable.create_record("GPSS PROPOSALBIO SCORES", {
                    "PROPOSAL": [proposal_id],
                    "REVISION": revision,
                    "BIOHACK NUMBER": bh["biohack_number"],
                    "BIOHACK NAME": bh["biohack_name"],
                    "SCORE": bh["score"],
                    "PASSFAIL": "Pass" if bh["score"] >= 6 else "Fail",
                    "DETAILS JSON": "",
                    "RECOMMENDATIONS": "",
                    "ANALYZED DATE": datetime.now().strftime("%Y-%m-%d"),
                })
            self.airtable.update_record("GPSS Proposals", proposal_id, {
                "PROPOSAL REVISION COURT": revision
            })
        except Exception as e:
            print(f"Warning: Could not save per-biohack scores: {e}")

        return {
            "status": "success",
            "proposal_id": proposal_id,
            "submission_gate": gate,
            **result,
        }

    def approve(self, proposal_id: str, approved_by: str, override_warnings: bool = False) -> Dict:
        """
        Approve proposal for submission
        
        Args:
            proposal_id: Airtable record ID
            approved_by: Name of approver
            override_warnings: Allow approval even if below threshold
            
        Returns:
            Approval result with timestamp and gate status
        """
        proposal = self._get_record_by_id("GPSS Proposals", proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}

        fields = proposal.get("fields", {})
        composite = float(fields.get("PROPOSALBIO COMPOSITE SCORE") or 0)
        status = fields.get("PROPOSALBIO STATUS") or ""

        # Check if approval allowed
        if not override_warnings:
            if composite < 75:
                return {"error": "Composite score below 75; cannot approve without override"}
            if status in ("REDRAFT", "REJECT"):
                return {"error": "Proposal has critical failures; cannot approve without override"}

        # Approve and unlock
        ts = datetime.utcnow().isoformat() + "Z"
        self.airtable.update_record("GPSS Proposals", proposal_id, {
            "PROPOSALBIO APPROVED BY": approved_by,
            "PROPOSAL APPROVED DATE": ts,
            "PROPOSALBIO GATE": "UNLOCKED",
            "STATUS": "Ready to Send",
        })

        return {
            "status": "approved",
            "proposal_id": proposal_id,
            "composite_score": composite,
            "approved_by": approved_by,
            "approved_timestamp": ts,
            "submission_unlocked": True,
        }

    def record_outcome(self, proposal_id: str, outcome: str, win_value: float = 0) -> Dict:
        """
        Record win/loss outcome for adaptive learning
        
        Args:
            proposal_id: Airtable record ID
            outcome: 'Won', 'Lost', 'No Decision'
            win_value: Contract value if won
            
        Returns:
            Learning record details
        """
        proposal = self._get_record_by_id("GPSS Proposals", proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}

        fields = proposal.get("fields", {})
        
        # Get biohack scores
        biohack_scores = json.loads(fields.get("PROPOSALBIO BIOHACK SCORE JSON") or "[]")
        scores_dict = {bh["biohack_number"]: bh["score"] for bh in biohack_scores}

        # Create learning record
        learning_data = {
            "PROPOSAL": [proposal_id],
            "OUTCOME": outcome,
            "WIN VALUE": win_value,
            "AGENCY TYPE": fields.get("AGENCY TYPE") or "",
            "REGION": fields.get("REGION") or "",
            "COMPOSITE SCORE": fields.get("PROPOSALBIO COMPOSITE SCORE") or 0,
            "BIOHACK 1 SCORE": scores_dict.get(1, 0),
            "BIOHACK 2 SCORE": scores_dict.get(2, 0),
            "BIOHACK 3 SCORE": scores_dict.get(3, 0),
            "BIOHACK 4 SCORE": scores_dict.get(4, 0),
            "BIOHACK 5 SCORE": scores_dict.get(5, 0),
            "BIOHACK 6 SCORE": scores_dict.get(6, 0),
            "BIOHACK 7 SCORE": scores_dict.get(7, 0),
            "BIOHACK 8 SCORE": scores_dict.get(8, 0),
            "BIOHACK 9 SCORE": scores_dict.get(9, 0),
            "BIOHACK 10 SCORE": scores_dict.get(10, 0),
            "RECORDED DATE": datetime.utcnow().isoformat() + "Z",
        }

        try:
            record = self.airtable.create_record("GPSS PROPOSAL BIO LEARNING", learning_data)
            return {
                "status": "success",
                "learning_record_id": record["id"],
                "message": "Outcome recorded for adaptive learning"
            }
        except Exception as e:
            return {"error": f"Could not save learning record: {str(e)}"}

    def _get_record_by_id(self, table: str, record_id: str) -> Optional[Dict]:
        """Get a single Airtable record by ID"""
        recs = self.airtable.search_records(table, f"RECORD_ID()='{record_id}'")
        return recs[0] if recs else None

    def _build_proposal_text(self, fields: Dict) -> str:
        """Combine all proposal sections into single text for analysis"""
        parts = [
            fields.get("EXECUTIVE SUMMARY", ""),
            fields.get("TECHNICAL APPROACH", ""),
            fields.get("STAFFING PLAN ", ""),
            fields.get("PAST PERFORMANCE", ""),
            fields.get("PRICING-JUSTIFICATION", ""),
        ]
        return "\n\n".join([p for p in parts if p])
