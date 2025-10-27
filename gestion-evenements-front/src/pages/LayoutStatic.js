// src/pages/LayoutStatic.js
import Home from "./Home"; // ⬅️ on importe ta page CRUD

export default function LayoutStatic() {
  return (
    <>
      {/* Topbar */}
      <nav className="sb-topnav navbar navbar-expand navbar-dark bg-dark">
        <a className="navbar-brand ps-3" href="/">Start Bootstrap</a>
        <button className="btn btn-link btn-sm order-1 order-lg-0 me-4 me-lg-0" id="sidebarToggle">
          <i className="fas fa-bars"></i>
        </button>
        <form className="d-none d-md-inline-block form-inline ms-auto me-0 me-md-3 my-2 my-md-0">
          <div className="input-group">
            <input className="form-control" type="text" placeholder="Search for..." aria-label="Search" />
            <button className="btn btn-primary" type="button"><i className="fas fa-search"></i></button>
          </div>
        </form>
        <ul className="navbar-nav ms-auto ms-md-0 me-3 me-lg-4">
          <li className="nav-item dropdown">
            {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
            <a className="nav-link dropdown-toggle" id="navbarDropdown" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              <i className="fas fa-user fa-fw"></i>
            </a>
            <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
              <li><a className="dropdown-item" href="#!">Settings</a></li>
              <li><a className="dropdown-item" href="#!">Activity Log</a></li>
              <li><hr className="dropdown-divider" /></li>
              <li><a className="dropdown-item" href="#!">Logout</a></li>
            </ul>
          </li>
        </ul>
      </nav>

      {/* Layout global */}
      <div id="layoutSidenav">
        {/* Sidebar */}
        <div id="layoutSidenav_nav">
          <nav className="sb-sidenav accordion sb-sidenav-dark" id="sidenavAccordion">
            <div className="sb-sidenav-menu">
              <div className="nav">
                <div className="sb-sidenav-menu-heading">CORE</div>
                <a className="nav-link" href="/">
                  <div className="sb-nav-link-icon"><i className="fas fa-tachometer-alt"></i></div>
                  Page d'acceuil
                </a>

                {/*<div className="sb-sidenav-menu-heading">INTERFACE</div>
                <a className="nav-link" href="/layout">
                  <div className="sb-nav-link-icon"><i className="fas fa-table"></i></div>
                  Static Layout
                </a>
              </div>*/}
              </div>
            </div>
            <div className="sb-sidenav-footer">
              <div className="small">Logged in as:</div>
              Admin
            </div>
          </nav>
        </div>

        {/* Contenu */}
        <div id="layoutSidenav_content">
          <main>
            {/* ⬇️ ICI on rend TON Home, dans le container du thème */}
            <div className="container-fluid px-4">
              <Home />
            </div>
          </main>

          <footer className="py-4 bg-light mt-auto">
            <div className="container-fluid px-4">
              <div className="d-flex align-items-center justify-content-between small">
                <div className="text-muted">© 2025 Your App</div>
                <div>
                  <a href="#!">Privacy Policy</a>
                  &middot;
                  <a href="#!">Terms &amp; Conditions</a>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </>
  );
}
