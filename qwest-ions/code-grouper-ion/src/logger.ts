import chalk from 'chalk';

export class Logger {
  info(msg: string) { console.log(chalk.blue('[INFO]'), msg); }
  success(msg: string) { console.log(chalk.green('[SUCCESS]'), msg); }
  warning(msg: string) { console.log(chalk.yellow('[WARNING]'), msg); }
  error(msg: string) { console.log(chalk.red('[ERROR]'), msg); }
  section(title: string) { console.log(chalk.bold.cyan(`\n${'='.repeat(60)}\n  ${title}\n${'='.repeat(60)}\n`)); }
  subsection(title: string) { console.log(chalk.bold(`\n${'-'.repeat(40)}\n  ${title}\n${'-'.repeat(40)}\n`)); }
  progress(current: number, total: number) {
    const pct = ((current / total) * 100).toFixed(1);
    process.stdout.write(`\r[${current}/${total}] ${pct}%`);
    if (current === total) console.log();
  }
}

export const logger = new Logger();
