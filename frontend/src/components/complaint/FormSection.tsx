interface FormSectionProps {
  title: string;
  children: React.ReactNode;
}

export default function FormSection({
  title,
  children,
}: FormSectionProps) {
  return (
    <section className="form-section">
      <div className="section-title">
        <span className="section-line" />
        <h3>{title}</h3>
      </div>

      <div className="form-grid">
        {children}
      </div>
    </section>
  );
}