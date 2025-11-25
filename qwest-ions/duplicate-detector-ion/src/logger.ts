import chalk from 'chalk';

export type LogLevel = 'info' | 'success' | 'warning' | 'error' | 'debug';

export class Logger {
  constructor(private ionName: string = 'Duplicate Detector Ion') {}

  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private log(level: LogLevel, message: string, data?: any): void {
    const timestamp = this.formatTimestamp();
    const prefix = `[${timestamp}] [${this.ionName}] [${level.toUpperCase()}]`;

    switch (level) {
      case 'info':
        console.log(chalk.blue(prefix), message);
        break;
      case 'success':
        console.log(chalk.green(prefix), message);
        break;
      case 'warning':
        console.log(chalk.yellow(prefix), message);
        break;
      case 'error':
        console.log(chalk.red(prefix), message);
        break;
      case 'debug':
        console.log(chalk.gray(prefix), message);
        break;
    }

    if (data) {
      console.log(chalk.gray(JSON.stringify(data, null, 2)));
    }
  }

  info(message: string, data?: any): void {
    this.log('info', message, data);
  }

  success(message: string, data?: any): void {
    this.log('success', message, data);
  }

  warning(message: string, data?: any): void {
    this.log('warning', message, data);
  }

  error(message: string, data?: any): void {
    this.log('error', message, data);
  }

  debug(message: string, data?: any): void {
    this.log('debug', message, data);
  }

  section(title: string): void {
    console.log(chalk.bold.cyan(`\n${'='.repeat(60)}`));
    console.log(chalk.bold.cyan(`  ${title}`));
    console.log(chalk.bold.cyan(`${'='.repeat(60)}\n`));
  }

  subsection(title: string): void {
    console.log(chalk.bold(`\n${'-'.repeat(40)}`));
    console.log(chalk.bold(`  ${title}`));
    console.log(chalk.bold(`${'-'.repeat(40)}\n`));
  }

  table(data: Record<string, any>): void {
    console.table(data);
  }

  progress(current: number, total: number, item?: string): void {
    const percentage = ((current / total) * 100).toFixed(1);
    const bar = '█'.repeat(Math.floor(current / total * 40));
    const empty = '░'.repeat(40 - bar.length);
    const itemText = item ? ` - ${item}` : '';

    process.stdout.write(
      `\r${chalk.cyan(`[${bar}${empty}]`)} ${percentage}% (${current}/${total})${itemText}`
    );

    if (current === total) {
      console.log(); // New line when complete
    }
  }
}

export const logger = new Logger();
