import Navbar from "../components/Navbar";
import HeroSection from "../components/HeroSection";
import Footer from "../components/Footer";

const HomePage = () => {
  const history = JSON.parse(localStorage.getItem("patternai_history") || "[]");
  return (
    <div style={{ minHeight: "100vh", background: "#f0fdfb" }}>
      <Navbar historyCount={history.length} />
      <HeroSection />
      <Footer />
    </div>
  );
};

export default HomePage;