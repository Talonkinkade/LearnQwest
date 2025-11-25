#!/usr/bin/env bun

import { parseArgs } from "util";
import { z } from "zod";

/**
 * Quiz Generator Ion - BMAD Method
 * Generates educational quiz questions from content with TEKS alignment
 */

// Input Schema
const InputSchema = z.object({
  content: z.string().min(50, "Content must be at least 50 characters"),
  topic: z.string().optional(),
  grade_level: z.string().default("6-8"),
  num_questions: z.number().min(1).max(20).default(5),
  question_types: z.array(
    z.enum(['multiple_choice', 'true_false', 'short_answer'])
  ).optional().default(['multiple_choice', 'true_false'])
});

// Output Schema
const OutputSchema = z.object({
  success: z.boolean(),
  result: z.object({
    topic: z.string(),
    grade_level: z.string(),
    questions: z.array(z.object({
      id: z.number(),
      type: z.string(),
      question: z.string(),
      options: z.array(z.string()).optional(),
      correct_answer: z.string(),
      explanation: z.string(),
      teks_alignment: z.string().optional(),
      difficulty: z.enum(['easy', 'medium', 'hard']).optional()
    }))
  }),
  metrics: z.object({
    execution_time_ms: z.number(),
    questions_generated: z.number(),
    content_length: z.number()
  })
});

type Input = z.infer<typeof InputSchema>;
type Output = z.infer<typeof OutputSchema>;

class QuizGenerator {
  private verbose: boolean;

  constructor(verbose: boolean = false) {
    this.verbose = verbose;
  }

  private log(message: string, data?: any) {
    if (this.verbose) {
      const timestamp = new Date().toISOString();
      console.error(`[${timestamp}] [QuizGenerator] ${message}`, data ? JSON.stringify(data) : '');
    }
  }

  async generate(input: Input): Promise<Output> {
    const startTime = Date.now();
    this.log('Starting quiz generation', { 
      topic: input.topic, 
      num_questions: input.num_questions,
      content_length: input.content.length
    });

    try {
      // Validate input
      const validated = InputSchema.parse(input);
      this.log('Input validated');

      // Extract key concepts from content
      const concepts = this.extractKeyConcepts(validated.content);
      this.log('Extracted key concepts', { count: concepts.length });

      // Generate questions
      const questions = this.generateQuestions(
        concepts,
        validated.content,
        validated.num_questions,
        validated.question_types,
        validated.grade_level
      );

      this.log('Questions generated', { count: questions.length });

      const result: Output = {
        success: true,
        result: {
          topic: validated.topic || this.inferTopic(validated.content),
          grade_level: validated.grade_level,
          questions
        },
        metrics: {
          execution_time_ms: Date.now() - startTime,
          questions_generated: questions.length,
          content_length: validated.content.length
        }
      };

      // Validate output
      return OutputSchema.parse(result);

    } catch (error) {
      this.log('Error during generation', error);
      return {
        success: false,
        result: { 
          topic: input.topic || 'Unknown', 
          grade_level: input.grade_level || '6-8', 
          questions: [] 
        },
        metrics: {
          execution_time_ms: Date.now() - startTime,
          questions_generated: 0,
          content_length: input.content?.length || 0
        }
      };
    }
  }

  private extractKeyConcepts(content: string): string[] {
    // Split into sentences
    const sentences = content
      .split(/[.!?]+/)
      .map(s => s.trim())
      .filter(s => s.length > 20 && s.length < 200);

    // Extract important sentences (first pass)
    const concepts = sentences.slice(0, 15);

    this.log('Extracted sentences', { count: concepts.length });
    return concepts;
  }

  private inferTopic(content: string): string {
    // Simple topic inference from first sentence
    const firstSentence = content.split(/[.!?]/)[0];
    const words = firstSentence.split(/\s+/).slice(0, 5);
    return words.join(' ');
  }

  private generateQuestions(
    concepts: string[],
    fullContent: string,
    numQuestions: number,
    types: string[],
    gradeLevel: string
  ): Array<any> {
    const questions = [];
    const actualNum = Math.min(numQuestions, concepts.length);

    for (let i = 0; i < actualNum; i++) {
      const concept = concepts[i];
      const type = types[i % types.length];

      let question;
      if (type === 'multiple_choice') {
        question = this.generateMultipleChoice(i + 1, concept, gradeLevel);
      } else if (type === 'true_false') {
        question = this.generateTrueFalse(i + 1, concept, gradeLevel);
      } else {
        question = this.generateShortAnswer(i + 1, concept, gradeLevel);
      }

      questions.push(question);
    }

    return questions;
  }

  private generateMultipleChoice(id: number, concept: string, gradeLevel: string): any {
    // Extract key terms
    const words = concept.split(/\s+/);
    const keyTerm = words.find(w => w.length > 6) || words[0];

    return {
      id,
      type: 'multiple_choice',
      question: `Based on the following concept: "${concept.substring(0, 80)}...", which statement is most accurate?`,
      options: [
        `The main idea relates to ${keyTerm}`,
        `This concept is unrelated to ${keyTerm}`,
        `${keyTerm} is not mentioned in this context`,
        `The opposite of ${keyTerm} is described`
      ],
      correct_answer: "A",
      explanation: `This question tests comprehension of: ${concept.substring(0, 100)}`,
      teks_alignment: this.getTEKSAlignment('science', gradeLevel, 'comprehension'),
      difficulty: 'medium'
    };
  }

  private generateTrueFalse(id: number, concept: string, gradeLevel: string): any {
    return {
      id,
      type: 'true_false',
      question: `True or False: ${concept.substring(0, 100)}`,
      options: ["True", "False"],
      correct_answer: "True",
      explanation: `This statement is directly from the content: ${concept.substring(0, 80)}`,
      teks_alignment: this.getTEKSAlignment('science', gradeLevel, 'recall'),
      difficulty: 'easy'
    };
  }

  private generateShortAnswer(id: number, concept: string, gradeLevel: string): any {
    const words = concept.split(/\s+/);
    const questionPhrase = words.slice(0, 8).join(' ');

    return {
      id,
      type: 'short_answer',
      question: `Explain in your own words: ${questionPhrase}`,
      correct_answer: concept.substring(0, 150),
      explanation: `Look for understanding of the key concept: ${concept.substring(0, 100)}`,
      teks_alignment: this.getTEKSAlignment('science', gradeLevel, 'application'),
      difficulty: 'hard'
    };
  }

  private getTEKSAlignment(subject: string, gradeLevel: string, skillType: string): string {
    // Simplified TEKS alignment (would be more sophisticated in production)
    const gradeNum = gradeLevel.split('-')[0] || '6';
    
    const alignments: Record<string, string> = {
      'recall': `TEKS.${subject}.${gradeNum}.1.A`,
      'comprehension': `TEKS.${subject}.${gradeNum}.2.B`,
      'application': `TEKS.${subject}.${gradeNum}.3.C`,
      'analysis': `TEKS.${subject}.${gradeNum}.4.D`
    };

    return alignments[skillType] || `TEKS.${subject}.${gradeNum}.1.A`;
  }
}

// CLI Entry Point
async function main() {
  const { values } = parseArgs({
    args: Bun.argv.slice(2),
    options: {
      input: { type: 'string', short: 'i' },
      output: { type: 'string', short: 'o' },
      content: { type: 'string', short: 'c' },
      topic: { type: 'string', short: 't' },
      num: { type: 'string', short: 'n' },
      grade: { type: 'string', short: 'g' },
      verbose: { type: 'boolean', short: 'v', default: false },
      help: { type: 'boolean', short: 'h', default: false }
    }
  });

  if (values.help) {
    console.log(`
Quiz Generator Ion - BMAD Method
Generate educational quiz questions from content

Usage:
  bun run src/index.ts [options]

Options:
  -i, --input   <file>    Input JSON file with content
  -o, --output  <file>    Output JSON file (default: stdout)
  -c, --content <text>    Direct content input
  -t, --topic   <text>    Topic name
  -n, --num     <number>  Number of questions (default: 5)
  -g, --grade   <level>   Grade level (default: 6-8)
  -v, --verbose           Verbose logging
  -h, --help              Show this help

Examples:
  # From file
  bun run src/index.ts -i content.json -o quiz.json

  # Direct content
  bun run src/index.ts -c "Photosynthesis is..." -t "Photosynthesis" -n 3

  # With options
  bun run src/index.ts -i content.json -g "9-12" -n 10 -v
    `);
    process.exit(0);
  }

  // Read input
  let inputData: Input;

  if (values.input) {
    // From file
    const fileContent = await Bun.file(values.input).text();
    inputData = JSON.parse(fileContent);
  } else if (values.content) {
    // From command line
    inputData = {
      content: values.content,
      topic: values.topic,
      num_questions: values.num ? parseInt(values.num) : 5,
      grade_level: values.grade || '6-8'
    };
  } else {
    // Default example
    inputData = {
      content: `Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce glucose and oxygen. This process occurs in chloroplasts, which contain chlorophyll. Chlorophyll is the green pigment that captures light energy. The light-dependent reactions occur in the thylakoid membranes, while the light-independent reactions (Calvin cycle) occur in the stroma. Plants are autotrophs, meaning they produce their own food through photosynthesis.`,
      topic: "Photosynthesis",
      grade_level: "6-8",
      num_questions: 5
    };
  }

  // Generate quiz
  const generator = new QuizGenerator(values.verbose);
  const output = await generator.generate(inputData);

  // Write output
  const outputJson = JSON.stringify(output, null, 2);

  if (values.output) {
    await Bun.write(values.output, outputJson);
    if (values.verbose) {
      console.error(`\n✅ Quiz written to: ${values.output}`);
      console.error(`   Questions generated: ${output.metrics.questions_generated}`);
      console.error(`   Execution time: ${output.metrics.execution_time_ms}ms`);
    }
  } else {
    console.log(outputJson);
  }

  process.exit(output.success ? 0 : 1);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
