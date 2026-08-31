import { Link } from "react-router-dom";
import Brand from "./Brand";
import { megaGroups } from "../config/publicRegistry";
import { site } from "../config/content";
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="shell footer-lead">
        <div>
          <Brand />
          <p>
            Evidence-led financial intelligence for traceable, controlled,
            human-reviewed investigation.
          </p>
        </div>
        <div>
          <p className="eyebrow">Associated organization</p>
          <p>{site.company}</p>
          <Link className="knowledge-link" to="/contact">
            Contact the project
          </Link>
        </div>
        <div>
          <p className="eyebrow">Technical reference</p>
          <Link className="knowledge-link" to="/docs/architecture">
            Read the architecture
          </Link>
          <Link className="knowledge-link" to="/docs/api">
            View the API contract
          </Link>
        </div>
      </div>
      <nav className="shell footer-map" aria-label="Complete site map">
        {megaGroups.map((group) => (
          <section key={group.label}>
            <h2>
              <Link to={group.featured}>{group.label}</Link>
            </h2>
            {group.columns
              .flatMap((c) => c[1])
              .map(([name, path], i) => (
                <Link to={path} key={`${path}-${i}`}>
                  {name}
                </Link>
              ))}
          </section>
        ))}
      </nav>
      <div className="shell footer-legal">
        <span>© {new Date().getFullYear()} Prysm Intelligence</span>
        <span>Version 0.1 · Financial intelligence software</span>
        <div>
          <Link to="/privacy">Privacy</Link>
          <Link to="/terms">Terms</Link>
          <Link to="/report/responsible-disclosure">
            Responsible disclosure
          </Link>
        </div>
      </div>
    </footer>
  );
}
