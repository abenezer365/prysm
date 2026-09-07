export class AppError extends Error {
  status;
  code;
  details;
  constructor(status, code, message, details) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}
export const notFound = (name) =>
  new AppError(404, "NOT_FOUND", `${name} not found`);
