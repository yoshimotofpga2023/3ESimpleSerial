# �����g�Z���T�[����p�V���A���ʐM���K�[
updated : 2026/02/03
## �g����

- arduino�i��H�쐬&�v���O�����������ݍς݁j��PC�Ɛڑ�����Ă��邱�Ƃ��m�F����D
- [connect]�{�^���������D����ŁAarudino�̃|�[�g��I��

    ���|�[�g���킩��Ȃ���΁Aarudino IDE�Ŋm�F����D

- [Start]�{�^���������đ�����J�n����D

    �����arduino����V���A���ʐM�Ńf�[�^�����M����Ă��邱�Ƃ�z�肷�邪�A���l�ȊO�̃f�[�^����M�����ꍇ��
    ��ʏ�ɐ����͕\������Ȃ��D

- �����f�[�^���\���Ɏ擾�ł�����[Stop]�{�^���������Čv������߂�

- �f�[�^�����������A���邢�͌v���_�����Ȃ��Ȃǂ�����x�v������ꍇ�́A���̂܂�[Start]�{�^�����ēx�����D

    ���O��v�����ꂽ�f�[�^�̓��Z�b�g�����D

- �擾�����f�[�^���e�ɖ�肪�Ȃ���΁A��ʂ̃f�[�^���R�s�[���APC�̃��������ɃR�s�y���A�K�v�ɉ�����
�f�[�^�����H���āACSV�`���Ńt�@�C����ۑ�����D�i�t�@�C�����̍Ō��.csv�Ƃ����OK�j

- �A�v�����I������Ƃ��͔O�̈�[disconnect]�{�^����������arduino��PC�̐ڑ����I�t�ɂ��Ă����D

## �d�l

### �v���O����

- Web Serial API��JavaScript�ŌĂяo���D
- [connect]�{�^���ŁA�w�肳�ꂽ�{�[���[�g��arduino�ƃV���A���ʐM���J�n����D
    - �񓯊�����(await)��arduino�Ɛڑ������݂�D�ڑ��ɐ�������΃V���A���ʐM���n�߂�D
    - �f�[�^�̎擾�� readLoop�֐��Œ�`���Ă���D
    ```
      async function readLoop() {
    const decoder = new TextDecoder();
    try {
      while (port && keepReading) {
        const r = port.readable.getReader();
        reader = r;
        try {
          while (true) {
            const { value, done } = await r.read();
            if (done) break;
            if (value) {
              const chunk = decoder.decode(value);
              ln(chunk.replace(/\r/g, "\\r").replace(/\n/g, "\\n\n"));
              rxBuffer += chunk;
              // �s���Ƃɏ���
              let idx;
              while ((idx = rxBuffer.search(/\r?\n/)) >= 0) {
                const line = rxBuffer.slice(0, idx);
                rxBuffer = rxBuffer.slice(idx + (rxBuffer[idx] === '\r' && rxBuffer[idx+1] === '\n' ? 2 : 1));
                const trimmed = line.trim();
                if (trimmed.length === 0) continue;
                if (isNumericLine(trimmed)) {
                  addDistanceLine(trimmed);
                }
              }
            }
          }
        } catch (e) {
          // �ǂݎ�蒆�f���Ȃ�
        } finally {
          r.releaseLock();
          if (!keepReading) break;
        }
      }
    } catch (e) {
      ln("[read error] " + e);
    }
  }
    ```
    �֐��̃|�C���g�́A���s�������ƂɃV���A���ʐM�̃f�[�^��ǂݎ�鏈�������Ă���D
    ���Ƃ��΁A123.4\r\n�Ƃ�����A123.4�݂̂�line�Ƃ����ϐ��Ɋi�[����D
    �f�[�^���`���K�v�Ȃ̂ŁA�ŏI�I��trimmed�Ƃ����ϐ��Ƀf�[�^������D

    �ŏI�I�ɁAaddDistance�Ƃ����֐��ŁA�f�[�^�̎擾���ԂƎ擾���������f�[�^��records�z���push����D��ʂɂ́A�����̂ݕ\������D

    - �ȉ��̐��K�\���Ŏ擾�����f�[�^���琔�l�݂̂��擾����D

    ```
    /^[\s]*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?[\s]*$/
    ```
    ��L�֐����AisNumericLine�֐��ŏ������Ă���D

- [Start]�{�^���ŁAarduino����V���A���ʐM�ő��M����Ă���f�[�^���擾����D
    - �O��v�������f�[�^������΃��Z�b�g�����D
    - 500ms�Ԋu��arduino�ɕ�����"D"���V���A���ʐM�ő��M���Ă���D
        - ���̎d�l�ɑΉ�����arduino�̃v���O�����ł���΁AD���󂯎�����ꍇ�̂݃V���A���ʐM�ő���f�[�^�𑗐M����Ƃ������W�b�N���쐬�ł���D


- [Stop]�{�^���ŁA�v�����I������D�܂��Aarduino�Ƃ̓V���A���ʐM���p�����Ă���D
    - Interval���荞�݂̒�~�ƁA���̊֐��ŕێ������timerID�I�u�W�F�N�g���������̈悩��������D

- [Disconnect]�{�^����arduino�Ƃ̃V���A���ڑ���ؒf����D

- �i�����؂̂��ߗ��p�񐄏��j[DownloadCSV]�{�^����CSV�`���ŉ��H���ꂽ�f�[�^���_�E�����[�h�����D

- ���̑�
    - �V���A���ʐM�̃f�[�^���H����Ă��Ȃ����̂́u�f�o�b�O�p���O�v��ʂɕ\������Ă���D
    - css�Ajavascript�͂��ׂāAhtml�t�@�C���ɋL�q����Ă���D

### ��
- Web�u���E�U(chrome, edge)�Ɉˑ�����Web Serial API�𗘗p�D
- �T�[�o�[�͖�����streamlit cloud���g�p�D���̂��߁A�T�[�o�[�@�\��Python(streamlit�Ɉˑ�����)
- �T�[�o�[�@�\�i�o�b�N�G���h�j��streamlit(python)�AUI�@�\�i�t�����g�G���h�A�V���A���ʐM�@�\�j��JavaScript(html��css)�ƁAUI�̑�g��streamlit(python)

