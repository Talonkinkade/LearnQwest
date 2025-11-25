import chalk from 'chalk';

export class Logger {
  info(msg: string) { console.log(chalk.blue('[INFO]'), msg); }
  success(msg: string) { console.log(chalk.green('[SUCCESS]'), msg); }
  warning(msg: string) { console.log(chalk.yellow('[WARNING]'), msg); }
  error(msg: string) { console.log(chalk.red('[ERROR]'), msg); }
  section(title: string) { console.log(chalk.bold.cyan(`\n${'='.repeat(70)}\n  ${title}\n${'='.repeat(70)}\n`)); }
  subsection(title: string) { console.log(chalk.bold(`\n${'-'.repeat(50)}\n  ${title}\n${'-'.repeat(50)}\n`)); }
}

export const logger = new Logger();
