"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const pg_1 = require("pg");
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
const url_1 = require("url");
// Load env vars
dotenv_1.default.config();
const __filename = (0, url_1.fileURLToPath)(import.meta.url);
const __dirname = path_1.default.dirname(__filename);
function runMigration() {
    return __awaiter(this, void 0, void 0, function* () {
        console.log('Starting Phase 1 migration (Scan Config & Presets)...');
        const connectionString = process.env.DATABASE_URL;
        if (!connectionString) {
            console.error('Error: DATABASE_URL not found in .env');
            process.exit(1);
        }
        const client = new pg_1.Client({
            connectionString: connectionString,
            ssl: { rejectUnauthorized: false }
        });
        try {
            yield client.connect();
            console.log('Connected to database.');
            const sqlPath = path_1.default.join(__dirname, 'supabase', 'phase1_scan_config.sql');
            const sql = fs_1.default.readFileSync(sqlPath, 'utf8');
            console.log(`Reading migration file: ${sqlPath}`);
            yield client.query(sql);
            console.log('Phase 1 Migration executed successfully!');
        }
        catch (err) {
            console.error('Migration failed:', err);
            process.exit(1);
        }
        finally {
            yield client.end();
        }
    });
}
runMigration();
