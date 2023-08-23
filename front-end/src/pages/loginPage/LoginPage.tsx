import { loginWithLine } from 'service/api/api';
import styles from './styles.module.css';

const LoginPage = () => {
  const lineLogin = async () => {
    try {
      const lineAuthoriseURL = await loginWithLine();
      if (lineAuthoriseURL?.url) {
        window.location.replace(lineAuthoriseURL?.url);
      }
    } catch (error) {}
  };

  return (
    <div className={styles.App}>
      {/* <Typography> Aime</Typography> */}
      <div onClick={() => lineLogin()} className={styles.lineButton} />
    </div>
  );
};

export default LoginPage;
