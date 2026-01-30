declare module 'robots-parser' {
  interface RobotsParser {
    isAllowed(url: string, ua?: string): boolean | undefined;
    isDisallowed(url: string, ua?: string): boolean | undefined;
    getMatchingLineNumber(url: string, ua?: string): number;
    getCrawlDelay(ua?: string): number | undefined;
    getSitemaps(): string[];
    getPreferredHost(): string | undefined;
  }

  function robotsParser(url: string, content: string): RobotsParser;
  export = robotsParser;
}
